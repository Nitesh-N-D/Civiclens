from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .corpus import SOURCES, public_source
from .gemini import GeminiProvider
from .models import AskRequest, AskResponse
from .service import RequestBudget, answer_question

app = FastAPI(title="CivicLens API", version="0.1.0", docs_url="/api/docs", redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

provider = GeminiProvider()
budget = RequestBudget()


@app.get("/api/health")
def health() -> dict[str, object]:
    return {"status": "ok", "provider": provider.public_status, "source_count": len(SOURCES)}


@app.get("/api/sources")
def sources() -> dict[str, list[dict[str, str]]]:
    return {"sources": [public_source(source) for source in SOURCES]}


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
