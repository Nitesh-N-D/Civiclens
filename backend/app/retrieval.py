"""Hybrid lexical and optional Gemini-vector retrieval over the active public corpus.

The corpus comes from corpus_store (PostgreSQL when configured, else the built-in records). The
lexical index is rebuilt whenever the active corpus object changes, so a database refresh takes
effect on the next question without a restart.
"""

import math
import threading
from collections import Counter
from dataclasses import dataclass, field

from . import corpus_store
from .config import settings
from .corpus import SourceChunk
from .gemini import GeminiProvider
from .text import STOPWORDS, matches, query_tokens, tokens  # noqa: F401 - re-exported

_matches = matches  # backwards-compatible name used by service.py and tests

# Absolute relevance floor on the raw lexical score. Calibrated on
# evaluation/retrieval_cases.json (10 Nov 2026): in-scope cases and probes score >= 1.3,
# off-topic probes score 0. Below this, CivicLens abstains instead of returning
# unrelated sources (TD-03).
MIN_LEXICAL_SCORE = 0.9
# Hits scoring below this share of the best hit are dropped as noise.
RELATIVE_CUTOFF = 0.3
# With embeddings enabled, a strong semantic match may rescue a lexical miss.
# Uncalibrated: re-check with a real embedding run before relying on it.
MIN_SEMANTIC_SCORE = 0.75


def _document_text(source: SourceChunk) -> str:
    return " ".join((source.title, source.text_en, source.text_ta, source.keywords))


@dataclass
class _Index:
    sources: tuple[SourceChunk, ...]
    counts: tuple[Counter, ...]
    average_length: float
    vectors: list[list[float]] | None = field(default=None)


_index_lock = threading.Lock()
_current: _Index | None = None


def _index() -> _Index:
    """Tokenise the active corpus once per corpus object (TD-14)."""
    global _current
    sources = corpus_store.active().sources
    with _index_lock:
        if _current is None or _current.sources is not sources:
            counts = tuple(Counter(tokens(_document_text(source))) for source in sources)
            average = max(1.0, sum(sum(c.values()) for c in counts) / max(1, len(counts)))
            _current = _Index(sources, counts, average)
        return _current


def _term_frequency(query_token: str, counts: Counter) -> int:
    return sum(count for doc_token, count in counts.items() if matches(query_token, doc_token))


def lexical_scores(query: str, index: _Index | None = None) -> list[float]:
    index = index or _index()
    terms = query_tokens(query)
    if not terms:
        return [0.0] * len(index.sources)
    frequencies = {term: [_term_frequency(term, counts) for counts in index.counts] for term in set(terms)}
    total = len(index.counts)
    scores: list[float] = []
    for position, counts in enumerate(index.counts):
        length = sum(counts.values())
        score = 0.0
        for term in terms:
            tf = frequencies[term][position]
            if not tf:
                continue
            doc_freq = sum(1 for value in frequencies[term] if value)
            inverse_frequency = math.log(1 + (total - doc_freq + 0.5) / (doc_freq + 0.5))
            denominator = tf + 1.2 * (0.25 + 0.75 * length / index.average_length)
            score += inverse_frequency * (tf * 2.2) / denominator
        scores.append(score)
    return scores


def keyword_covered(query: str, index: _Index) -> bool:
    """True when every query term matches a curated keyword of one source.

    Curated aliases are a deliberate relevance signal; this rescues short queries such as
    "scholarship" whose words are shared by several sources and so score below the absolute floor
    in a small corpus. A single unrelated word ("cricket") keeps the query below the floor.
    """
    terms = set(query_tokens(query))
    if not terms:
        return False
    for source in index.sources:
        keywords = set(tokens(source.keywords))
        if all(any(matches(term, keyword) for keyword in keywords) for term in terms):
            return True
    return False


def cosine_similarity(first: list[float], second: list[float]) -> float:
    if len(first) != len(second) or not first:
        return 0.0
    dot = sum(a * b for a, b in zip(first, second, strict=True))
    norm_first = math.sqrt(sum(a * a for a in first))
    norm_second = math.sqrt(sum(b * b for b in second))
    if not norm_first or not norm_second:
        return 0.0
    return dot / (norm_first * norm_second)


def _vectors(provider: GeminiProvider, index: _Index) -> list[list[float]] | None:
    if not settings.enable_embeddings or not provider.available:
        return None
    with _index_lock:
        if index.vectors is None:
            # Stored vectors from PostgreSQL when every source has one (no Gemini call);
            # otherwise embed once per corpus and keep the result in memory.
            stored = corpus_store.active().vectors
            if stored and all(source.id in stored for source in index.sources):
                index.vectors = [list(stored[source.id]) for source in index.sources]
            else:
                contents = [corpus_store.embedding_text(source) for source in index.sources]
                index.vectors = provider.embed(contents, "RETRIEVAL_DOCUMENT")
    return index.vectors


def retrieve(query: str, provider: GeminiProvider, limit: int = 4) -> list[tuple[SourceChunk, float]]:
    index = _index()
    lexical = lexical_scores(query, index)
    maximum = max(lexical, default=0.0)
    vector_scores: list[float] | None = None

    try:
        doc_vectors = _vectors(provider, index)
        if doc_vectors:
            query_vector = provider.embed([query], "RETRIEVAL_QUERY")[0]
            vector_scores = [cosine_similarity(query_vector, vector) for vector in doc_vectors]
    except Exception:
        # Semantic search is optional; lexical retrieval remains available.
        vector_scores = None

    best_semantic = max(vector_scores, default=0.0) if vector_scores else 0.0
    if maximum < MIN_LEXICAL_SCORE and best_semantic < MIN_SEMANTIC_SCORE and not keyword_covered(query, index):
        return []

    combined = []
    for position, source in enumerate(index.sources):
        lexical_part = lexical[position] / maximum if maximum else 0.0
        if vector_scores:
            score = 0.55 * lexical_part + 0.45 * max(0.0, vector_scores[position])
        else:
            score = lexical_part
        combined.append((source, score))
    combined.sort(key=lambda item: item[1], reverse=True)
    top = combined[0][1] if combined else 0.0
    return [item for item in combined[:limit] if item[1] > 0 and item[1] >= RELATIVE_CUTOFF * top]
