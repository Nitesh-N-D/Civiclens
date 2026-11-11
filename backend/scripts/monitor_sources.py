"""Check every active official source and record the result in source_checks.

Usage (from backend/):
    python scripts/monitor_sources.py --dry-run   # fetch and print; write nothing
    python scripts/monitor_sources.py             # record one automated check per source

Run weekly (see .github/workflows/source-monitor.yml). 'changed' rows appear on the maintainer
page for review; published records are never edited by this script.
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import connect  # noqa: E402
from app.monitoring import classify, fetch  # noqa: E402

_LAST_HASH = """
SELECT content_hash FROM source_checks
WHERE source_id = %s AND content_hash IS NOT NULL AND note LIKE 'automated:%%'
ORDER BY checked_at DESC LIMIT 1
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    with connect() as conn:
        sources = conn.execute("SELECT id, canonical_url FROM sources WHERE active ORDER BY id").fetchall()
        previous = {sid: (conn.execute(_LAST_HASH, (sid,)).fetchone() or (None,))[0] for sid, _ in sources}
    counts: dict[str, int] = {}
    for source_id, url in sources:
        result = fetch(url)
        outcome, digest, note = classify(result, previous[source_id])
        counts[outcome] = counts.get(outcome, 0) + 1
        print(f"{outcome:13} {source_id}  ({note.removeprefix('automated: ')})")
        if not args.dry_run:
            with connect() as conn:
                conn.execute(
                    "INSERT INTO source_checks (source_id, outcome, response_status, content_hash, note)"
                    " VALUES (%s, %s, %s, %s, %s)",
                    (source_id, outcome, result.status, digest, note),
                )
        time.sleep(2)  # be gentle with government servers
    print(", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) or "no active sources")
    # A changed source is expected work for a reviewer, not a failure; unreachable ones are reported.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
