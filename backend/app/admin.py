"""Maintainer actions backed by PostgreSQL. Every change writes an audit_log row in the same
transaction, so a change without its audit record cannot happen."""

import json

from .auth import Principal
from .db import connect

CHECK_OUTCOMES = ("reachable", "changed", "unreachable", "manual_review")


def record_source_check(principal: Principal, source_id: str, outcome: str, note: str) -> dict:
    if outcome not in CHECK_OUTCOMES:
        raise ValueError("unknown outcome")
    with connect() as conn, conn.transaction():
        exists = conn.execute("SELECT 1 FROM sources WHERE id = %s", (source_id,)).fetchone()
        if not exists:
            raise LookupError(source_id)
        row = conn.execute(
            "INSERT INTO source_checks (source_id, outcome, note) VALUES (%s, %s, %s) RETURNING id, checked_at",
            (source_id, outcome, note),
        ).fetchone()
        conn.execute(
            "INSERT INTO audit_log (actor_user_id, actor_email, action, entity_type, entity_id, detail)"
            " VALUES (%s, %s, 'source_check_recorded', 'source', %s, %s::jsonb)",
            (principal.user_id, principal.email, source_id, json.dumps({"outcome": outcome, "check_id": row[0]})),
        )
    return {"id": row[0], "source_id": source_id, "outcome": outcome, "checked_at": row[1].isoformat()}


def recent_checks(limit: int = 20) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, source_id, outcome, note, checked_at FROM source_checks ORDER BY checked_at DESC LIMIT %s",
            (limit,),
        ).fetchall()
    return [
        {"id": r[0], "source_id": r[1], "outcome": r[2], "note": r[3], "checked_at": r[4].isoformat()} for r in rows
    ]


def recent_audit(limit: int = 20) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, actor_email, action, entity_type, entity_id, detail, created_at"
            " FROM audit_log ORDER BY created_at DESC LIMIT %s",
            (limit,),
        ).fetchall()
    return [
        {
            "id": r[0],
            "actor": r[1],
            "action": r[2],
            "entity_type": r[3],
            "entity_id": r[4],
            "detail": r[5],
            "created_at": r[6].isoformat(),
        }
        for r in rows
    ]
