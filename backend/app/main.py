from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .changes import CHANGES, public_change
from .config import settings
from .corpus import SOURCES, public_schemes, public_source
from .db import database_status
from .gemini import GeminiProvider
from .models import AskRequest, AskResponse
from .security import valid_bearer_token
from .service import AnswerCache, ClientLimiter, PersistentBudget, answer_question

app = FastAPI(title="CivicLens API", version="0.1.0", docs_url="/api/docs", redoc_url=None)
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
    if request.url.path == "/api/ask":
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
        "source_count": len(SOURCES),
        "admin_enabled": bool(settings.admin_token),
        "database": database_status(),
    }


@app.get("/api/sources")
def sources() -> dict[str, list[dict[str, str | None]]]:
    return {"sources": [public_source(source) for source in SOURCES]}


@app.get("/api/schemes")
def schemes(language: str = "en"):
    selected_language = "ta" if language == "ta" else "en"
    return {"schemes": [scheme.model_dump() for scheme in public_schemes(selected_language)]}


@app.get("/api/changes")
def changes(language: str = "en") -> dict[str, list[dict[str, str]]]:
    selected_language = "ta" if language == "ta" else "en"
    return {"changes": [public_change(change, selected_language) for change in CHANGES]}


@app.get("/api/admin/overview")
def admin_overview(authorization: str | None = Header(default=None)) -> dict[str, object]:
    expected = settings.admin_token
    if not valid_bearer_token(expected, authorization):
        raise HTTPException(status_code=404, detail="Not found")
    source_rows = [public_source(source) for source in SOURCES]
    return {
        "sources": source_rows,
        "source_count": len(source_rows),
        "human_verified_count": sum(row["human_verified_at"] is not None for row in source_rows),
        "review_pending_count": sum(row["human_verified_at"] is None for row in source_rows),
        "provider": provider.public_status,
        "monitoring": "not_configured",
        "mutations_enabled": False,
    }


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
