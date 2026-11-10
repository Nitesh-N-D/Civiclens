"""Give a Supabase Auth account a maintainer role, change it, or remove it.

Usage (from backend/):
    python scripts/grant_role.py someone@example.org reviewer
    python scripts/grant_role.py someone@example.org --revoke

Create the account first in the Supabase dashboard (Authentication > Users > Add user) and turn
off public sign-up. Roles: viewer (read the overview), reviewer (record source checks),
maintainer (reserved for role management and publishing). Each change is written to audit_log.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.auth import ROLE_RANK  # noqa: E402
from app.db import connect  # noqa: E402

SCRIPT_ACTOR = "00000000-0000-0000-0000-000000000000"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("email")
    parser.add_argument("role", nargs="?", choices=sorted(ROLE_RANK))
    parser.add_argument("--revoke", action="store_true")
    args = parser.parse_args()
    if not args.revoke and not args.role:
        parser.error("give a role or --revoke")

    with connect() as conn, conn.transaction():
        user = conn.execute("SELECT id, email FROM auth.users WHERE lower(email) = lower(%s)", (args.email,)).fetchone()
        if not user:
            print("No Supabase Auth account with that email. Add the user in the dashboard first.")
            return 1
        user_id, email = user
        if args.revoke:
            conn.execute("DELETE FROM admin_roles WHERE user_id = %s", (user_id,))
            action, detail = "role_revoked", {}
        else:
            conn.execute(
                "INSERT INTO admin_roles (user_id, email, role) VALUES (%s, %s, %s)"
                " ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, email = EXCLUDED.email, updated_at = NOW()",
                (user_id, email, args.role),
            )
            action, detail = "role_granted", {"role": args.role}
        conn.execute(
            "INSERT INTO audit_log (actor_user_id, actor_email, action, entity_type, entity_id, detail)"
            " VALUES (%s, 'scripts/grant_role.py', %s, 'admin_role', %s, %s::jsonb)",
            (SCRIPT_ACTOR, action, str(user_id), json.dumps(detail)),
        )
    print(f"{action}: {email}" + (f" -> {args.role}" if args.role else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
