"""Maintainer authentication (TD-09).

Two ways in:
- Supabase Auth sign-in (SUPABASE_URL + SUPABASE_PUBLISHABLE_KEY + DATABASE_URL). The access token
  is checked by asking Supabase who it belongs to (so sign-out and revocation take effect), and
  the role comes from the admin_roles table. Required for every change.
- CIVICLENS_ADMIN_TOKEN, a static token for local development. It only ever grants 'viewer'.

Tokens are never logged; the short cache is keyed by a hash of the token.
"""

import hashlib
import json
import logging
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from .config import settings
from .security import valid_bearer_token

log = logging.getLogger("civiclens.auth")

ROLE_RANK = {"viewer": 1, "reviewer": 2, "maintainer": 3}
_CACHE_SECONDS = 60
_cache: dict[str, tuple[float, "Principal | None"]] = {}
_cache_lock = threading.Lock()


@dataclass(frozen=True)
class Principal:
    user_id: str
    email: str
    role: str
    via: str  # "supabase" or "static_token"

    def can(self, role: str) -> bool:
        return ROLE_RANK.get(self.role, 0) >= ROLE_RANK[role]


def sign_in_configured() -> bool:
    return bool(settings.supabase_url and settings.supabase_publishable_key and settings.database_url)


def _bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].casefold() != "bearer" or not parts[1].strip():
        return None
    return parts[1].strip()


def supabase_user(token: str) -> dict | None:
    """Ask Supabase Auth whose token this is. None for an invalid, expired or revoked token."""
    request = urllib.request.Request(
        f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
        headers={"Authorization": f"Bearer {token}", "apikey": settings.supabase_publishable_key},
    )
    try:
        with urllib.request.urlopen(request, timeout=6) as response:
            user = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code in (401, 403):
            return None
        log.warning("supabase auth check failed: HTTP %s", error.code)
        raise
    except (TimeoutError, urllib.error.URLError, OSError, ValueError) as error:
        log.warning("supabase auth check failed: %s", type(error).__name__)
        raise
    return user if isinstance(user, dict) and user.get("id") else None


def role_for(user_id: str) -> str | None:
    from .db import connect

    with connect() as conn:
        row = conn.execute("SELECT role FROM admin_roles WHERE user_id = %s", (user_id,)).fetchone()
    return row[0] if row else None


def _resolve_supabase(token: str) -> "Principal | None":
    key = hashlib.sha256(token.encode("utf-8")).hexdigest()
    now = time.monotonic()
    with _cache_lock:
        cached = _cache.get(key)
        if cached and now - cached[0] < _CACHE_SECONDS:
            return cached[1]
    user = supabase_user(token)
    principal = None
    if user:
        role = role_for(str(user["id"]))
        if role in ROLE_RANK:
            principal = Principal(str(user["id"]), str(user.get("email") or ""), role, "supabase")
    with _cache_lock:
        if len(_cache) > 256:
            _cache.clear()
        _cache[key] = (now, principal)
    return principal


def authenticate(authorization: str | None) -> "Principal | None":
    """The caller's principal, or None. Errors talking to Supabase count as not signed in."""
    if settings.admin_token and valid_bearer_token(settings.admin_token, authorization):
        return Principal("static-token", "local maintainer token", "viewer", "static_token")
    token = _bearer(authorization)
    if not token or not sign_in_configured():
        return None
    try:
        return _resolve_supabase(token)
    except Exception:  # noqa: BLE001 - fail closed; the reason is already logged without the token
        return None


def clear_cache() -> None:
    with _cache_lock:
        _cache.clear()
