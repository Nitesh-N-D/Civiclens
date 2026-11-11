from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import admin, corpus_store, eligibility
from .auth import Principal, authenticate, sign_in_configured
from .changes import public_change
from .config import settings
from .corpus import public_schemes, public_source
from .db import database_status
from .gemini import GeminiProvider
from .models import AskRequest, AskResponse, EligibilityRequest, SourceCheckRequest
from .service import AnswerCache, ClientLimiter, PersistentBudget, answer_question


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Load the corpus from PostgreSQL when configured; otherwise stay on the built-in records.
    corpus_store.enable_database()
    yield


app = FastAPI(title="CivicLens API", version="0.1.0", docs_url="/api/docs", redoc_url=None, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# TD-08: requests are small JSON documents; reject anything far larger before parsing.
MAX_BODY_BYTES = 16_384
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cross-Origin-Resource-Policy": "same-origin",
}
# The API serves JSON only; the interactive docs page needs its own scripts, so it is exempt.
API_CSP = "default-src 'none'; frame-ancestors 'none'"
DOCS_PATHS = ("/api/docs", "/api/openapi.json")


@app.middleware("http")
async def guard_requests(request: Request, call_next):
    length = request.headers.get("content-length")
    if length is not None and (not length.isdigit() or int(length) > MAX_BODY_BYTES):
        return JSONResponse({"detail": "Request too large"}, status_code=413)
    response = await call_next(request)
    for name, value in SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    if not request.url.path.startswith(DOCS_PATHS):
        response.headers.setdefault("Content-Security-Policy", API_CSP)
    if request.url.path in ("/api/ask", "/api/eligibility"):
        response.headers["Cache-Control"] = "no-store"
    return response


provider = GeminiProvider()
budget = PersistentBudget()
client_limiter = ClientLimiter()
answer_cache = AnswerCache()


def _client_id(request: Request) -> str:
    if settings.trust_forwarded_for:
        forwarded = request.headers.get("x-forwarded-for", "")
        first = forwarded.split(",")[0].strip()
        if first:
            return first
    return request.client.host if request.client else "unknown"


@app.get("/api/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "provider": provider.public_status,
        "source_count": len(corpus_store.active().sources),
        "corpus": corpus_store.active().origin,
        "admin_enabled": bool(settings.admin_token) or sign_in_configured(),
        # Public by design (Supabase publishable key); lets the maintainer page sign in.
        "admin_sign_in": (
            {"url": settings.supabase_url, "publishable_key": settings.supabase_publishable_key}
            if sign_in_configured()
            else None
        ),
        "database": database_status(),
    }


@app.get("/api/sources")
def sources() -> dict[str, list[dict[str, str | None]]]:
    return {"sources": [public_source(source) for source in corpus_store.active().sources]}


@app.get("/api/schemes")
def schemes(language: str = "en"):
    selected_language = "ta" if language == "ta" else "en"
    return {"schemes": [scheme.model_dump() for scheme in public_schemes(selected_language)]}


@app.get("/api/changes")
def changes(language: str = "en") -> dict[str, list[dict[str, str]]]:
    selected_language = "ta" if language == "ta" else "en"
    return {"changes": [public_change(change, selected_language) for change in corpus_store.active().changes]}


def _cited_sources(source_ids: set[str]) -> list[dict[str, str | None]]:
    return [public_source(s) for s in corpus_store.active().sources if s.id in source_ids]


def _available_schemes(requested: list[str]) -> list[str]:
    known = [scheme_id for scheme_id in corpus_store.active().schemes if scheme_id in eligibility.CRITERIA]
    return [scheme_id for scheme_id in requested if scheme_id in known] if requested else known


@app.get("/api/eligibility/questions")
def eligibility_questions(language: str = "en") -> dict[str, object]:
    return {"questions": eligibility.questions("ta" if language == "ta" else "en")}


@app.post("/api/eligibility")
def eligibility_check(payload: EligibilityRequest) -> dict[str, object]:
    """Deterministic screening; nothing is stored, logged or sent to Gemini."""
    results = [eligibility.assess(s, payload.profile, payload.language) for s in _available_schemes(payload.scheme_ids)]
    cited = {row["source_id"] for result in results for row in result["criteria"]}
    return {"results": results, "sources": _cited_sources(cited)}


@app.get("/api/schemes/compare")
def compare(ids: str = "", language: str = "en") -> dict[str, object]:
    requested = [part for part in ids.split(",") if part][:4]
    rows = eligibility.compare_rows(_available_schemes(requested), "ta" if language == "ta" else "en")
    return {"schemes": rows, "sources": _cited_sources({row["source_id"] for row in rows})}


def _require(authorization: str | None, role: str) -> Principal:
    """404 for anyone without access, so the admin surface is not discoverable."""
    principal = authenticate(authorization)
    if principal is None:
        raise HTTPException(status_code=404, detail="Not found")
    if not principal.can(role):
        raise HTTPException(status_code=403, detail="Your role cannot do this")
    return principal


def _can_write(principal: Principal) -> bool:
    return principal.via == "supabase" and principal.can("reviewer")


@app.get("/api/admin/overview")
def admin_overview(authorization: str | None = Header(default=None)) -> dict[str, object]:
    principal = _require(authorization, "viewer")
    source_rows = [public_source(source) for source in corpus_store.active().sources]
    checks: list[dict] = []
    audit: list[dict] = []
    if settings.database_url:
        try:
            checks, audit = admin.recent_checks(), admin.recent_audit()
        except Exception:  # noqa: BLE001 - the overview still works without the database
            checks, audit = [], []
    return {
        "you": {"email": principal.email, "role": principal.role, "via": principal.via},
        "sources": source_rows,
        "source_count": len(source_rows),
        "human_verified_count": sum(row["human_verified_at"] is not None for row in source_rows),
        "review_pending_count": sum(row["human_verified_at"] is None for row in source_rows),
        "provider": provider.public_status,
        "monitoring": "manual_checks" if settings.database_url else "not_configured",
        "recent_checks": checks,
        "recent_audit": audit,
        "mutations_enabled": _can_write(principal),
    }


@app.post("/api/admin/sources/{source_id}/checks", status_code=201)
def record_source_check(
    source_id: str, payload: SourceCheckRequest, authorization: str | None = Header(default=None)
) -> dict[str, object]:
    principal = _require(authorization, "reviewer")
    if not _can_write(principal):
        raise HTTPException(status_code=403, detail="Changes need a Supabase sign-in")
    try:
        return admin.record_source_check(principal, source_id, payload.outcome, payload.note.strip())
    except LookupError:
        raise HTTPException(status_code=404, detail="Unknown source") from None


@app.post("/api/ask", response_model=AskResponse)
def ask(payload: AskRequest, request: Request) -> AskResponse:
    if not client_limiter.allow(
        _client_id(request), settings.client_requests_per_minute, settings.client_daily_request_limit
    ):
        raise HTTPException(status_code=429, detail="Too many questions; please wait a minute.",
                            headers={"Retry-After": "60"})
    return answer_question(
        payload.question,
        payload.language,
        provider,
        budget,
        settings.requests_per_minute,
        settings.daily_request_limit,
        answer_cache,
    )
