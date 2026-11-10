"""The active public corpus: PostgreSQL when configured and populated, else the built-in records.

The API starts on the built-in records (app/corpus.py, app/changes.py). When DATABASE_URL is set,
startup and then a refresh every ten minutes load sources, schemes and change notices from the
database (seeded by scripts/seed_corpus.py). A database that is down, empty or returns invalid
rows never breaks answering: the last good corpus stays active.
"""

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any

from .changes import CHANGES, SchemeChange
from .config import settings
from .corpus import SCHEMES, SOURCES, SourceChunk

log = logging.getLogger("civiclens.corpus")

REFRESH_SECONDS = 600
RETRY_SECONDS = 60


@dataclass(frozen=True)
class Corpus:
    sources: tuple[SourceChunk, ...]
    schemes: dict[str, dict[str, Any]]
    changes: tuple[SchemeChange, ...]
    origin: str  # "built_in" or "database"


BUILT_IN = Corpus(SOURCES, SCHEMES, CHANGES, "built_in")

_active = BUILT_IN
_database_enabled = False
_next_refresh = 0.0
_refresh_lock = threading.Lock()


def active() -> Corpus:
    if _database_enabled and time.monotonic() >= _next_refresh:
        refresh()
    return _active


def enable_database() -> None:
    """Called at API startup. Tests and scripts stay on the built-in corpus unless they opt in."""
    global _database_enabled
    _database_enabled = bool(settings.database_url)
    if _database_enabled:
        refresh()


def reset() -> None:
    """Back to the built-in corpus with database loading off (used by tests)."""
    global _active, _database_enabled, _next_refresh
    _active, _database_enabled, _next_refresh = BUILT_IN, False, 0.0


def refresh() -> Corpus:
    global _active, _next_refresh
    if not _refresh_lock.acquire(blocking=False):
        return _active  # another request is already refreshing
    try:
        try:
            loaded = load_from_database()
        except Exception as exc:  # noqa: BLE001 - keep serving the last good corpus
            log.warning("corpus refresh failed: %s", type(exc).__name__)
            _next_refresh = time.monotonic() + RETRY_SECONDS
            return _active
        if loaded is None:
            log.info("database corpus is empty; keeping the %s corpus", _active.origin)
        else:
            _active = loaded
        _next_refresh = time.monotonic() + REFRESH_SECONDS
        return _active
    finally:
        _refresh_lock.release()


_SOURCES_SQL = """
SELECT c.id, d.title, d.canonical_url, s.owner, c.locator, s.status_label,
       c.text_en, c.text_ta, v.fetched_at, v.human_verified_at, c.keywords
FROM evidence_chunks c
JOIN documents d ON d.id = c.document_id
JOIN source_versions v ON v.id = d.version_id
JOIN sources s ON s.id = v.source_id
WHERE c.active AND s.active AND v.review_status NOT IN ('retired', 'contested')
ORDER BY s.display_order, c.id
"""

_SCHEMES_SQL = """
SELECT id, name_en, name_ta, department, department_ta, category, category_ta,
       overview_en, overview_ta, source_id
FROM schemes
WHERE publication_status <> 'retired' AND source_id IS NOT NULL
ORDER BY id
"""

_CHANGES_SQL = """
SELECT id, scheme_name_en, scheme_name_ta, match_names, evidence_status, change_type,
       summary_en, summary_ta, source_title, source_url, checked_at
FROM scheme_changes
WHERE scheme_name_en IS NOT NULL
ORDER BY checked_at DESC, id
"""


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    return value.date().isoformat() if hasattr(value, "date") else value.isoformat()


def source_from_row(row: tuple) -> SourceChunk | None:
    """Build a SourceChunk from a database row, or None when the row is unsafe to cite."""
    (chunk_id, title, url, owner, locator, status, text_en, text_ta, fetched_at, verified_at,
     keywords) = row
    if not (chunk_id and title and owner and locator) or not str(url).startswith("https://"):
        return None
    if not (text_en or "").strip() and not (text_ta or "").strip():
        return None
    return SourceChunk(
        id=chunk_id,
        title=title,
        url=url,
        owner=owner,
        locator=locator,
        status=status or "Review pending · confirm with the department",
        text_en=text_en or "",
        text_ta=text_ta or "",
        desk_checked_at=_iso(fetched_at) or "not recorded",
        human_verified_at=_iso(verified_at),
        keywords=keywords or "",
    )


def scheme_from_row(row: tuple) -> tuple[str, dict[str, Any]]:
    (scheme_id, name_en, name_ta, dept_en, dept_ta, cat_en, cat_ta, over_en, over_ta, source_id) = row
    return scheme_id, {
        "title_en": name_en,
        "title_ta": name_ta or name_en,
        "department_en": dept_en,
        "department_ta": dept_ta or dept_en,
        "category_en": cat_en,
        "category_ta": cat_ta or cat_en,
        "overview_en": over_en or "",
        "overview_ta": over_ta or over_en or "",
        "source_id": source_id,
    }


def change_from_row(row: tuple) -> SchemeChange | None:
    (change_id, name_en, name_ta, names, status, change_type, summary_en, summary_ta,
     source_title, source_url, checked_at) = row
    if status not in ("official", "reported") or not str(source_url).startswith("https://"):
        return None
    return SchemeChange(
        id=change_id,
        scheme_en=name_en,
        scheme_ta=name_ta or name_en,
        names=tuple(names or ()),
        status=status,
        change_type=change_type,
        summary_en=summary_en,
        summary_ta=summary_ta,
        source_title=source_title,
        source_url=source_url,
        checked_at=_iso(checked_at) or "",
    )


def load_from_database() -> Corpus | None:
    """Read the corpus; None when the database holds no citable sources."""
    from .db import connect

    with connect() as conn:
        source_rows = conn.execute(_SOURCES_SQL).fetchall()
        scheme_rows = conn.execute(_SCHEMES_SQL).fetchall()
        change_rows = conn.execute(_CHANGES_SQL).fetchall()
    sources = tuple(s for s in map(source_from_row, source_rows) if s is not None)
    if len(sources) < len(source_rows):
        log.warning("skipped %d invalid source rows", len(source_rows) - len(sources))
    if not sources:
        return None
    source_ids = {s.id for s in sources}
    schemes = dict(r for r in map(scheme_from_row, scheme_rows) if r[1]["source_id"] in source_ids)
    changes = tuple(c for c in map(change_from_row, change_rows) if c is not None)
    return Corpus(sources, schemes, changes, "database")
