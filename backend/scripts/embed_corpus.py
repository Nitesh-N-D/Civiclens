"""Store Gemini document embeddings in evidence_chunks.embedding_768 (pgvector).

Usage (from backend/):
    python scripts/embed_corpus.py --dry-run   # list chunks that need a vector; no Gemini call
    python scripts/embed_corpus.py             # embed them and store the vectors

A chunk needs a vector when it has none, or when its text or GEMINI_EMBEDDING_MODEL changed since
the stored one was made (tracked by embedding_text_hash, migration 0006). Uses one
batchEmbedContents call per 50 chunks, counted against the free-tier quota like any other call.
With the vectors stored and GEMINI_ENABLE_EMBEDDINGS=true, the API reads them instead of embedding
the whole corpus after every restart; each question still costs one query-embedding call.
Re-run after scripts/seed_corpus.py changes any text.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import corpus_store  # noqa: E402
from app.config import settings  # noqa: E402
from app.db import connect  # noqa: E402
from app.gemini import GeminiProvider  # noqa: E402

BATCH = 50


def pending(sources, rows) -> list:
    current = corpus_store.vectors_from_rows(rows, sources)
    return [source for source in sources if source.id not in current]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    corpus = corpus_store.load_from_database()
    if corpus is None:
        print("No citable sources in the database. Run scripts/seed_corpus.py first.")
        return 1
    with connect() as conn:
        rows = conn.execute(corpus_store._VECTORS_SQL).fetchall()
    todo = pending(corpus.sources, rows)
    print(f"{len(corpus.sources)} active chunks; {len(todo)} need a {settings.embedding_model} vector.")
    for source in todo:
        print(f"  {source.id}")
    if args.dry_run or not todo:
        return 0

    provider = GeminiProvider()
    if not provider.available:
        print("Gemini is not configured or is cooling down; nothing stored.")
        return 1
    stored = 0
    for start in range(0, len(todo), BATCH):
        batch = todo[start:start + BATCH]
        vectors = provider.embed([corpus_store.embedding_text(s) for s in batch], "RETRIEVAL_DOCUMENT")
        if any(len(v) != 768 for v in vectors):
            print("Unexpected vector size from Gemini; nothing stored for this batch.")
            return 1
        with connect() as conn, conn.transaction():
            for source, vector in zip(batch, vectors, strict=True):
                conn.execute(
                    "UPDATE evidence_chunks SET embedding_768 = %s::vector, embedding_model = %s,"
                    " embedding_text_hash = %s WHERE id = %s",
                    ("[" + ",".join(f"{v:.8f}" for v in vector) + "]", settings.embedding_model,
                     corpus_store.embedding_text_hash(source), source.id),
                )
        stored += len(batch)
    print(f"Stored {stored} vectors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
