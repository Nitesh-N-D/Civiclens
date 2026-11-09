from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .corpus import SOURCES, public_schemes, public_source
from .gemini import GeminiProvider
from .models import AskRequest, AskResponse
from .security import valid_bearer_token
from .service import RequestBudget, answer_question

app = FastAPI(title="CivicLens API", version="0.1.0", docs_url="/api/docs", redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

provider = GeminiProvider()
budget = RequestBudget()


@app.get("/api/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "provider": provider.public_status,
        "source_count": len(SOURCES),
        "admin_enabled": bool(settings.admin_token),
    }


@app.get("/api/sources")
def sources() -> dict[str, list[dict[str, str | None]]]:
    return {"sources": [public_source(source) for source in SOURCES]}


@app.get("/api/schemes")
def schemes(language: str = "en"):
    selected_language = "ta" if language == "ta" else "en"
    return {"schemes": [scheme.model_dump() for scheme in public_schemes(selected_language)]}


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
def ask(payload: AskRequest) -> AskResponse:
    return answer_question(
        payload.question,
        payload.language,
        provider,
        budget,
        settings.requests_per_minute,
        settings.daily_request_limit,
    )
