import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


def _split_list(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


@dataclass(frozen=True)
class Settings:
    gemini_key_1: str = os.getenv("GEMINI_API_KEY_1", "").strip()
    gemini_key_2: str = os.getenv("GEMINI_API_KEY_2", "").strip()
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    embedding_model: str = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001").strip()
    enable_embeddings: bool = os.getenv("GEMINI_ENABLE_EMBEDDINGS", "false").lower() == "true"
    requests_per_minute: int = max(1, int(os.getenv("GEMINI_REQUESTS_PER_MINUTE", "10")))
    daily_request_limit: int = max(1, int(os.getenv("GEMINI_DAILY_REQUEST_LIMIT", "100")))
    allowed_origins: tuple[str, ...] = _split_list(
        os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    )


settings = Settings()
