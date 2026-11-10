"""Copy the built-in corpus (app/corpus.py, app/changes.py) into PostgreSQL. Safe to re-run.

Usage (from backend/, after scripts/migrate.py):  python scripts/seed_corpus.py

- Sources, schemes and change notices are upserted by id.
- Each distinct source text becomes one source_versions row (keyed by content hash), so editing a
  record and re-seeding keeps the previous version as history instead of overwriting it.
- New versions start as 'review_pending'; this script never marks anything human-approved.
- Rows that exist only in the database are left untouched.
Everything runs in one transaction: a failure leaves the database as it was.
"""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.changes import CHANGES  # noqa: E402
from app.corpus import SCHEMES, SOURCES, SourceChunk  # noqa: E402
from app.db import connect  # noqa: E402

JURISDICTION = "Tamil Nadu"


def content_hash(source: SourceChunk) -> str:
    parts = (source.title, source.url, source.locator, source.text_en, source.text_ta, source.keywords)
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def seed_source(conn, order: int, source: SourceChunk) -> bool:
    """Upsert one source; returns True when a new version was created."""
    languages = [code for code, text in (("en", source.text_en), ("ta", source.text_ta)) if text]
    conn.execute(
        """
        INSERT INTO sources (id, owner, jurisdiction, canonical_url, source_type, language_codes,
                             access_method, status_label, display_order)
        VALUES (%s, %s, %s, %s, 'official_webpage', %s, 'manual_desk_review', %s, %s)
        ON CONFLICT (id) DO UPDATE SET owner = EXCLUDED.owner, canonical_url = EXCLUDED.canonical_url,
            language_codes = EXCLUDED.language_codes, status_label = EXCLUDED.status_label,
            display_order = EXCLUDED.display_order, updated_at = NOW()
        """,
        (source.id, source.owner, JURISDICTION, source.url, languages, source.status, order),
    )
    digest = content_hash(source)
    existing = conn.execute(
        "SELECT id FROM source_versions WHERE source_id = %s AND content_hash = %s", (source.id, digest)
    ).fetchone()
    if existing:
        version_id, created = existing[0], False
    else:
        version_id = conn.execute(
            """
            INSERT INTO source_versions (source_id, fetched_at, content_hash, review_status, human_verified_at)
            VALUES (%s, %s, %s, 'review_pending', %s) RETURNING id
            """,
            (source.id, source.desk_checked_at, digest, source.human_verified_at),
        ).fetchone()[0]
        created = True
    document = conn.execute(
        "SELECT id FROM documents WHERE version_id = %s ORDER BY id LIMIT 1", (version_id,)
    ).fetchone()
    if document:
        document_id = document[0]
    else:
        document_id = conn.execute(
            """
            INSERT INTO documents (version_id, title, canonical_url, media_type, language_code)
            VALUES (%s, %s, %s, 'text/html', %s) RETURNING id
            """,
            (version_id, source.title, source.url, languages[0] if languages else "en"),
        ).fetchone()[0]
    conn.execute(
        """
        INSERT INTO evidence_chunks (id, document_id, locator, text_en, text_ta, keywords, active)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        ON CONFLICT (id) DO UPDATE SET document_id = EXCLUDED.document_id, locator = EXCLUDED.locator,
            text_en = EXCLUDED.text_en, text_ta = EXCLUDED.text_ta, keywords = EXCLUDED.keywords
        """,
        (source.id, document_id, source.locator, source.text_en or None, source.text_ta or None, source.keywords),
    )
    return created


def seed_schemes(conn) -> None:
    for scheme_id, r in SCHEMES.items():
        source_url = next(s.url for s in SOURCES if s.id == r["source_id"])
        conn.execute(
            """
            INSERT INTO schemes (id, name_en, name_ta, department, department_ta, jurisdiction, category,
                                 category_ta, overview_en, overview_ta, source_id, official_route_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET name_en = EXCLUDED.name_en, name_ta = EXCLUDED.name_ta,
                department = EXCLUDED.department, department_ta = EXCLUDED.department_ta,
                category = EXCLUDED.category, category_ta = EXCLUDED.category_ta,
                overview_en = EXCLUDED.overview_en, overview_ta = EXCLUDED.overview_ta,
                source_id = EXCLUDED.source_id, official_route_url = EXCLUDED.official_route_url,
                updated_at = NOW()
            """,
            (scheme_id, r["title_en"], r["title_ta"], r["department_en"], r["department_ta"], JURISDICTION,
             r["category_en"], r["category_ta"], r["overview_en"], r["overview_ta"], r["source_id"], source_url),
        )


def seed_changes(conn) -> None:
    for c in CHANGES:
        conn.execute(
            """
            INSERT INTO scheme_changes (id, change_type, evidence_status, summary_en, summary_ta, source_title,
                                        source_url, checked_at, scheme_name_en, scheme_name_ta, match_names)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET change_type = EXCLUDED.change_type,
                evidence_status = EXCLUDED.evidence_status, summary_en = EXCLUDED.summary_en,
                summary_ta = EXCLUDED.summary_ta, source_title = EXCLUDED.source_title,
                source_url = EXCLUDED.source_url, checked_at = EXCLUDED.checked_at,
                scheme_name_en = EXCLUDED.scheme_name_en, scheme_name_ta = EXCLUDED.scheme_name_ta,
                match_names = EXCLUDED.match_names
            """,
            (c.id, c.change_type, c.status, c.summary_en, c.summary_ta, c.source_title, c.source_url,
             c.checked_at, c.scheme_en, c.scheme_ta, list(c.names)),
        )


def main() -> int:
    with connect() as conn, conn.transaction():
        new_versions = sum(seed_source(conn, order, source) for order, source in enumerate(SOURCES))
        seed_schemes(conn)
        seed_changes(conn)
    print(f"Seeded {len(SOURCES)} sources ({new_versions} new versions), {len(SCHEMES)} schemes, "
          f"{len(CHANGES)} change notices.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
