"""Hybrid lexical and optional Gemini-vector retrieval over the small public corpus."""

import math
import re
import threading
from collections import Counter

from .config import settings
from .corpus import SOURCES, SourceChunk
from .gemini import GeminiProvider

TOKEN_RE = re.compile(r"[\w஀-௿]+", re.UNICODE)
_cache_lock = threading.Lock()
_document_vectors: list[list[float]] | None = None

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
PREFIX_MIN_LENGTH = 5

# Function words and words that occur in almost every Tamil Nadu scheme query,
# which on their own say nothing about relevance.
STOPWORDS = frozenset(
    """a an the is are was were be been am im me my we our us you your he she it its they them their this that
    these those of in on at to for from by with and or not no do does did can could will would should may might
    what which who whom whose when where why how any some all there here get got give need want about also
    tamil nadu tn government govt scheme schemes current please tell know available apply""".split()
) | frozenset(
    "நான் என் எனது எனக்கு எங்கள் நாங்கள் என்ன எப்படி எங்கே எந்த யார் ஏதாவது உள்ளது உண்டா ஒரு மற்றும் "
    "தமிழ்நாடு தமிழ்நாட்டின் தமிழ்நாட்டில் அரசு திட்டம் திட்டங்கள் கிடைக்கும் வேண்டும் பற்றி இருக்கிறதா".split()
)


def _stem(token: str) -> str:
    # Light English plural folding; applied identically to queries and documents.
    if token.isascii() and len(token) > 4:
        if token.endswith("ies"):
            return token[:-3] + "y"
        if token.endswith("es") and token[-3] in "sxz":
            return token[:-2]
        if token.endswith("s") and not token.endswith("ss"):
            return token[:-1]
    return token


def tokens(text: str) -> list[str]:
    return [_stem(token.casefold()) for token in TOKEN_RE.findall(text) if len(token) > 1]


def query_tokens(text: str) -> list[str]:
    return [token for token in tokens(text) if token not in STOPWORDS]


def _matches(query_token: str, doc_token: str) -> bool:
    if query_token == doc_token:
        return True
    # Prefix match handles Tamil case suffixes (கல்லூரி / கல்லூரியில்) and English
    # inflection (scholarship / scholarships) without a morphology library.
    shorter, longer = sorted((query_token, doc_token), key=len)
    return len(shorter) >= PREFIX_MIN_LENGTH and longer.startswith(shorter)


def _document_text(source: SourceChunk) -> str:
    return " ".join((source.title, source.text_en, source.text_ta, source.keywords))


# The corpus is static, so tokenise it once at import (TD-14).
_DOC_COUNTS: tuple[Counter, ...] = tuple(Counter(tokens(_document_text(source))) for source in SOURCES)
_AVERAGE_LENGTH = max(1.0, sum(sum(counts.values()) for counts in _DOC_COUNTS) / max(1, len(_DOC_COUNTS)))


def _term_frequency(query_token: str, counts: Counter) -> int:
    return sum(count for doc_token, count in counts.items() if _matches(query_token, doc_token))


def lexical_scores(query: str) -> list[float]:
    terms = query_tokens(query)
    if not terms:
        return [0.0] * len(SOURCES)
    frequencies = {term: [_term_frequency(term, counts) for counts in _DOC_COUNTS] for term in set(terms)}
    total = len(_DOC_COUNTS)
    scores: list[float] = []
    for index, counts in enumerate(_DOC_COUNTS):
        length = sum(counts.values())
        score = 0.0
        for term in terms:
            tf = frequencies[term][index]
            if not tf:
                continue
            doc_freq = sum(1 for value in frequencies[term] if value)
            inverse_frequency = math.log(1 + (total - doc_freq + 0.5) / (doc_freq + 0.5))
            denominator = tf + 1.2 * (0.25 + 0.75 * length / _AVERAGE_LENGTH)
            score += inverse_frequency * (tf * 2.2) / denominator
        scores.append(score)
    return scores


def cosine_similarity(first: list[float], second: list[float]) -> float:
    if len(first) != len(second) or not first:
        return 0.0
    dot = sum(a * b for a, b in zip(first, second))
    norm_first = math.sqrt(sum(a * a for a in first))
    norm_second = math.sqrt(sum(b * b for b in second))
    if not norm_first or not norm_second:
        return 0.0
    return dot / (norm_first * norm_second)


def _vectors(provider: GeminiProvider) -> list[list[float]] | None:
    global _document_vectors
    if not settings.enable_embeddings or not provider.available:
        return None
    with _cache_lock:
        if _document_vectors is None:
            contents = [source.text_en + "\n" + source.text_ta for source in SOURCES]
            _document_vectors = provider.embed(contents, "RETRIEVAL_DOCUMENT")
    return _document_vectors


def retrieve(query: str, provider: GeminiProvider, limit: int = 4) -> list[tuple[SourceChunk, float]]:
    lexical = lexical_scores(query)
    maximum = max(lexical, default=0.0)
    vector_scores: list[float] | None = None

    try:
        doc_vectors = _vectors(provider)
        if doc_vectors:
            query_vector = provider.embed([query], "RETRIEVAL_QUERY")[0]
            vector_scores = [cosine_similarity(query_vector, vector) for vector in doc_vectors]
    except Exception:
        # Semantic search is optional; lexical retrieval remains available.
        vector_scores = None

    best_semantic = max(vector_scores, default=0.0) if vector_scores else 0.0
    if maximum < MIN_LEXICAL_SCORE and best_semantic < MIN_SEMANTIC_SCORE:
        return []

    combined = []
    for index, source in enumerate(SOURCES):
        lexical_part = lexical[index] / maximum if maximum else 0.0
        if vector_scores:
            score = 0.55 * lexical_part + 0.45 * max(0.0, vector_scores[index])
        else:
            score = lexical_part
        combined.append((source, score))
    combined.sort(key=lambda item: item[1], reverse=True)
    top = combined[0][1] if combined else 0.0
    return [item for item in combined[:limit] if item[1] > 0 and item[1] >= RELATIVE_CUTOFF * top]
