"""Apply pending SQL migrations to DATABASE_URL, in filename order, each exactly once.

Usage (from backend/):  python scripts/migrate.py [--status]
Each migration file opens and commits its own transaction and records itself in
schema_migrations, so a failed file leaves no partial state and is retried on the next run.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import connect  # noqa: E402

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


def applied_versions(conn) -> set[str]:
    exists = conn.execute("SELECT to_regclass('public.schema_migrations') IS NOT NULL").fetchone()[0]
    if not exists:
        return set()
    return {row[0] for row in conn.execute("SELECT migration_version FROM schema_migrations")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", action="store_true", help="list migrations without applying")
    args = parser.parse_args()
    files = sorted(MIGRATIONS.glob("[0-9][0-9][0-9][0-9]_*.sql"))
    with connect() as conn:
        done = applied_versions(conn)
        pending = [f for f in files if f.stem not in done]
        for f in files:
            print(f"{'applied ' if f.stem in done else 'pending '} {f.name}")
        if args.status or not pending:
            print("Nothing to apply." if not pending else f"{len(pending)} pending.")
            return 0
        for f in pending:
            print(f"Applying {f.name} ...")
            try:
                conn.execute(f.read_text(encoding="utf-8"))
            except Exception:
                conn.execute("ROLLBACK")
                print(f"FAILED on {f.name}; nothing from this file was kept.", file=sys.stderr)
                raise
    print("All migrations applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
