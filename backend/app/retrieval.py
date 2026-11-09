"""Hybrid lexical and optional Gemini-vector retrieval over the small public corpus."""

import math
import re
import threading
from collections import Counter

from .config import settings
from .corpus import SOURCES, SourceChunk
from .gemini import GeminiProvider

TOKEN_RE = re.compile(r"[\w\u0B80-\u0BFF]+", re.UNICODE)
_cache_lock = threading.Lock()
_document_vectors: list[list[float]] | None = None


def tokens(text: str) -> list[str]:
    return [token.casefold() for token in TOKEN_RE.findall(text) if len(token) > 1]


def lexical_scores(query: str) -> list[float]:
    query_tokens = tokens(query)
    docs = [tokens(source.text_en + " " + source.text_ta + " " + source.title) for source in SOURCES]
    if not query_tokens:
        return [0.0] * len(SOURCES)

    doc_freq = Counter(token for token in set(query_tokens) for doc in docs if token in set(doc))
    scores: list[float] = []
    average_length = max(1.0, sum(len(doc) for doc in docs) / len(docs))
    for doc in docs:
        counts = Counter(doc)
        score = 0.0
        for token in query_tokens:
            tf = counts[token]
            if not tf:
                continue
            inverse_frequency = math.log(1 + (len(docs) - doc_freq[token] + 0.5) / (doc_freq[token] + 0.5))
            denominator = tf + 1.2 * (0.25 + 0.75 * len(doc) / average_length)
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
    normalized_lexical = [score / maximum if maximum else 0.0 for score in lexical]
    vector_scores: list[float] | None = None

    try:
        doc_vectors = _vectors(provider)
        if doc_vectors:
            query_vector = provider.embed([query], "RETRIEVAL_QUERY")[0]
            vector_scores = [cosine_similarity(query_vector, vector) for vector in doc_vectors]
    except Exception:
        # Semantic search is optional; lexical retrieval remains available.
        vector_scores = None

    combined = []
    for index, source in enumerate(SOURCES):
        semantic = vector_scores[index] if vector_scores else 0.0
        score = 0.55 * normalized_lexical[index] + 0.45 * max(0.0, semantic)
        combined.append((source, score))
    combined.sort(key=lambda item: item[1], reverse=True)
    return [item for item in combined[:limit] if item[1] > 0]
