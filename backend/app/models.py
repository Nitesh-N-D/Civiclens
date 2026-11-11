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


class ChangeNotice(BaseModel):
    id: str
    scheme: str
    status: Literal["official", "reported"]
    summary: str
    source_title: str
    source_url: str
    checked_at: str


class AskResponse(BaseModel):
    text: str
    citations: list[Citation]
    mode: Literal["ai", "search"]
    warning: str
    notices: list[ChangeNotice] = Field(default_factory=list)


class SourceCheckRequest(BaseModel):
    outcome: str = Field(pattern="^(reachable|changed|unreachable|manual_review)$")
    note: str = Field(min_length=3, max_length=500)


class EligibilityRequest(BaseModel):
    # Coarse, voluntary choices only (see eligibility.PROFILE_FIELDS); unknown keys are ignored.
    profile: dict[str, str] = Field(default_factory=dict, max_length=12)
    scheme_ids: list[str] = Field(default_factory=list, max_length=10)
    language: Literal["en", "ta"] = "en"
