"""Optional PostgreSQL (Supabase) access.

The API runs without a database. When DATABASE_URL is set, the shared daily Gemini budget is
persisted so it survives free-tier restarts (Render sleeps when idle). Any database error falls
back to the in-memory budget; the database is never required to answer a question.
"""

import logging
import time
from datetime import UTC, datetime

from .config import settings

log = logging.getLogger("civiclens.db")

try:  # psycopg is only needed when DATABASE_URL is configured.
    import psycopg
except ImportError:  # pragma: no cover - exercised only in minimal installs
    psycopg = None


def connect():
    """Open a short-lived connection. prepare_threshold=None keeps Supabase's pooler happy."""
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not configured")
    if psycopg is None:
        raise RuntimeError("psycopg is not installed")
    return psycopg.connect(settings.database_url, connect_timeout=5, prepare_threshold=None, autocommit=True)


_STATUS_TTL_SECONDS = 60
_status_cache: tuple[float, str] | None = None
_budget_retry_at = 0.0


def database_status() -> str:
    """'not_configured', 'connected' or 'unavailable'. Never returns connection details.

    Cached for a minute so frequent host health checks do not open a connection each time.
    """
    global _status_cache
    if not settings.database_url:
        return "not_configured"
    now = time.monotonic()
    if _status_cache and now - _status_cache[0] < _STATUS_TTL_SECONDS:
        return _status_cache[1]
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
        status = "connected"
    except Exception as exc:  # noqa: BLE001 - status only; the error class is logged, not the URL
        log.warning("database health check failed: %s", type(exc).__name__)
        status = "unavailable"
    _status_cache = (now, status)
    return status


def claim_daily_slot(bucket: str, per_day: int) -> bool | None:
    """Atomically take one unit of today's budget.

    Returns True when allowed, False when the persisted daily limit is reached, and None when
    the database is not configured or unreachable (the caller then uses its in-memory count).
    """
    global _budget_retry_at
    if not settings.database_url or time.monotonic() < _budget_retry_at:
        return None
    today = datetime.now(UTC).date()
    try:
        with connect() as conn:
            row = conn.execute(
                """
                INSERT INTO api_usage_daily (usage_day, bucket, request_count)
                VALUES (%s, %s, 1)
                ON CONFLICT (usage_day, bucket) DO UPDATE
                    SET request_count = api_usage_daily.request_count + 1, updated_at = NOW()
                    WHERE api_usage_daily.request_count < %s
                RETURNING request_count
                """,
                (today, bucket, per_day),
            ).fetchone()
        return row is not None
    except Exception as exc:  # noqa: BLE001 - degrade to memory, never fail the request
        log.warning("persistent budget unavailable: %s", type(exc).__name__)
        # Do not make every question wait on a dead database; retry after a pause.
        _budget_retry_at = time.monotonic() + _STATUS_TTL_SECONDS
        return None
