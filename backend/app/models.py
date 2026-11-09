from typing import Literal

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1200)
    language: Literal["en", "ta"] = "en"


class Citation(BaseModel):
    id: str
    title: str
    url: str
    owner: str
    locator: str | None = None
    status: str
    desk_checked_at: str | None = None
    human_verified_at: str | None = None


class AnswerClaim(BaseModel):
    text: str
    citation_ids: list[str] = Field(min_length=1, max_length=5)


class GeneratedAnswer(BaseModel):
    claims: list[AnswerClaim] = Field(default_factory=list, max_length=8)
    unable_to_answer: bool = False


class SchemeCard(BaseModel):
    id: str
    title: str
    department: str
    category: str
    overview: str
    url: str
    source_id: str
    status: str
    eligibility_enabled: bool = False


class AskResponse(BaseModel):
    text: str
    citations: list[Citation]
    mode: Literal["ai", "search"]
    warning: str
