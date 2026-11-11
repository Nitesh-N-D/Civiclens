"""Scheduled official-source checks (Module G).

Fetches each active source page politely (robots.txt respected, one request per source, size and
time limits), hashes its visible text and compares it with the last automated check. A change is
recorded as 'changed' for a human to review; nothing published is edited automatically.
"""

import hashlib
import html
import re
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from dataclasses import dataclass

USER_AGENT = "CivicLens-source-monitor/0.1 (+independent public-information project; weekly checks)"
MAX_BYTES = 2_000_000
TIMEOUT_SECONDS = 20

_DROP = re.compile(r"<(script|style|noscript|svg|template)\b.*?</\1\s*>", re.IGNORECASE | re.DOTALL)
_TAGS = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class FetchResult:
    status: int | None
    body: bytes
    error: str | None = None


def visible_text(raw: bytes) -> str:
    """Page text without markup, scripts or whitespace differences, so cosmetic edits don't count."""
    text = raw.decode("utf-8", errors="replace")
    text = _TAGS.sub(" ", _DROP.sub(" ", text))
    return _SPACE.sub(" ", html.unescape(text)).strip()


def content_hash(raw: bytes) -> str:
    return hashlib.sha256(visible_text(raw).encode("utf-8")).hexdigest()


def classify(result: FetchResult, previous_hash: str | None) -> tuple[str, str | None, str]:
    """(outcome, content_hash, note) for a source_checks row."""
    if result.error or result.status is None or result.status >= 400:
        return "unreachable", None, f"automated: {result.error or f'HTTP {result.status}'}"
    digest = content_hash(result.body)
    if not visible_text(result.body):
        return "manual_review", digest, "automated: page has no readable text (script-rendered or empty)"
    if previous_hash is None:
        return "reachable", digest, "automated: first fingerprint recorded"
    if digest != previous_hash:
        return "changed", digest, "automated: visible text changed since the last check; review before updating"
    return "reachable", digest, "automated: unchanged"


def allowed_by_robots(url: str) -> bool:
    parts = urllib.parse.urlsplit(url)
    parser = urllib.robotparser.RobotFileParser(f"{parts.scheme}://{parts.netloc}/robots.txt")
    try:
        parser.read()
    except (urllib.error.URLError, OSError, ValueError):
        return True  # no readable robots.txt: the standard treats this as no restriction
    return parser.can_fetch(USER_AGENT, url)


def fetch(url: str) -> FetchResult:
    if not url.startswith("https://"):
        return FetchResult(None, b"", "not an https URL")
    if not allowed_by_robots(url):
        return FetchResult(None, b"", "disallowed by robots.txt")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.5"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310 - https only
            return FetchResult(response.status, response.read(MAX_BYTES + 1)[:MAX_BYTES])
    except urllib.error.HTTPError as error:
        return FetchResult(error.code, b"")
    except (urllib.error.URLError, OSError, ValueError) as error:
        reason = getattr(error, "reason", error)
        return FetchResult(None, b"", type(reason).__name__ if not isinstance(reason, str) else reason[:120])
