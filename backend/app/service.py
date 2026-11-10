import re
import unicodedata
from datetime import UTC, datetime, timedelta
from threading import Lock

from .changes import matching_changes, public_change
from .corpus import public_source
from .gemini import GeminiProvider, ProviderFailure
from .models import AskResponse, ChangeNotice, Citation
from .retrieval import _matches, query_tokens, retrieve, tokens

# Identifiers and secrets are refused before retrieval or generation. Situational
# context ("I am a student", "நான் கல்லூரியில் படிக்கிறேன்", "I am 67") is the core
# use case and is allowed (TD-01); it only triggers an extra privacy reminder.
SENSITIVE_PATTERNS = (
    re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),                      # Aadhaar-shaped number
    re.compile(r"\b\d{9,18}\b"),                                          # account/ID-length digit run
    re.compile(r"[௦-௯]{9,}"),                                               # same, in Tamil numerals
    re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.I),                        # PAN
    re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b"),               # Indian mobile
    re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", re.I),                          # IFSC
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Z]{2,}\b", re.I),                   # email
    re.compile(
        r"\b(?:my|our)\s+(?:aadhaar|aadhar|uid|pan|passport|voter\s*id|ration\s*card|bank|account|ifsc|upi|otp|"
        r"password|pin|phone|mobile|address)\s*(?:number|no\.?|id|details?)?\s*(?:is|=|:)",
        re.I,
    ),
    re.compile(r"\b(?:otp|password|passcode|pin)\s*(?:is|=|:)\s*\S+", re.I),
    re.compile(r"(?:என்|எனது|எங்கள்)\s*(?:ஆதார்|வங்கி|கணக்கு|கைபேசி|தொலைபேசி|முகவரி|கடவுச்சொல்)"),
    re.compile(r"(?:ஆதார்\s*எண்|கணக்கு\s*எண்|ஓடிபி|OTP)\s*[:=]?\s*[\d௦-௯]"),
)

PERSONAL_CONTEXT_PATTERNS = (
    re.compile(r"\b(?:I\s+am|I'm|my|our|we\s+are)\b", re.I),
    re.compile(r"(?:நான்|என்|எனது|எனக்கு|எங்கள்|எங்களுக்கு)"),
)
CONTEXT_NOTE = (
    " You don’t need to share personal details: questions may be processed by Google’s Gemini free tier."
)
TA_CONTEXT_NOTE = (
    " தனிப்பட்ட விவரங்களைப் பகிரத் தேவையில்லை: கேள்விகள் Google Gemini இலவச சேவையால் செயலாக்கப்படலாம்."
)

WARNING = (
    "Directory information is for discovery only. CivicLens Tamil wording has not been checked by a Tamil subject "
    "specialist. Confirm current rules and application status with the responsible department; CivicLens does not "
    "determine eligibility."
)
PRIVACY_RESPONSE = (
    "For privacy, please remove personal identifiers and private details, then ask a general question. "
    "This pilot does not need identity documents or personal records."
)
NO_EVIDENCE = (
    "I couldn’t find enough reviewed information to answer that safely. These official directory sources are only "
    "starting points; please confirm current rules with the responsible department."
)
TA_WARNING = (
    "திட்டக் கோப்பகத் தகவல் வழிகாட்டுதலுக்காக மட்டுமே. CivicLens தமிழ் விளக்கத்தை தமிழ் நிபுணர் "
    "சான்றாய்வு செய்யவில்லை. தற்போதைய விதிகளையும் விண்ணப்ப நிலையையும் சம்பந்தப்பட்ட துறையிடம் "
    "உறுதிப்படுத்தவும்; CivicLens தகுதியைத் தீர்மானிக்காது."
)
TA_PRIVACY_RESPONSE = (
    "தனியுரிமைக்காக, தனிப்பட்ட அடையாளங்களையும் விவரங்களையும் நீக்கி பொதுவான கேள்வியாகக் கேளுங்கள். "
    "இந்த முன்னோட்டத்திற்கு அடையாள ஆவணங்கள் அல்லது தனிப்பட்ட பதிவுகள் தேவையில்லை."
)
TA_NO_EVIDENCE = (
    "பாதுகாப்பாகப் பதிலளிக்கத் தேவையான சரிபார்க்கப்பட்ட தகவல் கிடைக்கவில்லை. இவை தகவல் கண்டறியும் "
    "அதிகாரப்பூர்வ ஆதாரங்கள் மட்டுமே; தற்போதைய விதிகளை சம்பந்தப்பட்ட துறையிடம் உறுதிப்படுத்தவும்."
)


# TD-07: a cheap claim-to-evidence gate. Not entailment, but it rejects the most harmful
# failure (an amount, age or date that is not in the cited source) and claims that share
# almost no content words with what they cite.
DIGIT_RUN = re.compile(r"\d+")
MIN_CLAIM_OVERLAP = 0.25


def _numbers(text: str) -> set[str]:
    ascii_digits = "".join(str(unicodedata.digit(ch)) if ch.isdigit() else ch for ch in text)
    joined = re.sub(r"(?<=\d),(?=\d)", "", ascii_digits)  # 1,200 -> 1200
    return {run.lstrip("0") or "0" for run in DIGIT_RUN.findall(joined)}


def claim_is_supported(claim: str, evidence_texts: list[str]) -> bool:
    evidence = " ".join(evidence_texts)
    if not _numbers(claim) <= _numbers(evidence):
        return False
    claim_tokens = set(query_tokens(claim))
    if not claim_tokens:
        return False
    evidence_tokens = set(tokens(evidence))
    supported = sum(any(_matches(token, other) for other in evidence_tokens) for token in claim_tokens)
    return supported / len(claim_tokens) >= MIN_CLAIM_OVERLAP


class RequestBudget:
    def __init__(self) -> None:
        self._lock = Lock()
        self._minute: list[datetime] = []
        self._day = datetime.now(UTC).date()
        self._daily = 0

    def allow(self, per_minute: int, per_day: int) -> bool:
        now = datetime.now(UTC)
        cutoff = now - timedelta(minutes=1)
        with self._lock:
            self._minute = [stamp for stamp in self._minute if stamp > cutoff]
            if self._day != now.date():
                self._day = now.date()
                self._daily = 0
            if len(self._minute) >= per_minute or not self._take_daily(per_day):
                return False
            self._minute.append(now)
            return True

    def _take_daily(self, per_day: int) -> bool:
        if self._daily >= per_day:
            return False
        self._daily += 1
        return True


class PersistentBudget(RequestBudget):
    """Shared Gemini budget whose daily count lives in PostgreSQL when DATABASE_URL is set.

    The per-minute window stays in memory (one Render instance). If the database is missing or
    unreachable, the in-memory daily count is used, so answers never depend on the database.
    """

    def __init__(self, bucket: str = "gemini") -> None:
        super().__init__()
        self._bucket = bucket

    def _take_daily(self, per_day: int) -> bool:
        from .db import claim_daily_slot

        persisted = claim_daily_slot(self._bucket, per_day)
        if persisted is None:
            return super()._take_daily(per_day)
        return persisted


class ClientLimiter:
    """Per-client sliding limits so one visitor cannot drain the shared free-tier quota."""

    def __init__(self, max_clients: int = 5000) -> None:
        self._lock = Lock()
        self._clients: dict[str, RequestBudget] = {}
        self._max_clients = max_clients

    def allow(self, client: str, per_minute: int, per_day: int) -> bool:
        with self._lock:
            budget = self._clients.get(client)
            if budget is None:
                if len(self._clients) >= self._max_clients:
                    self._clients.clear()  # bounded memory; resets are acceptable for a pilot
                budget = self._clients[client] = RequestBudget()
        return budget.allow(per_minute, per_day)


def contains_sensitive_details(text: str) -> bool:
    return any(pattern.search(text) for pattern in SENSITIVE_PATTERNS)


def mentions_personal_context(text: str) -> bool:
    return any(pattern.search(text) for pattern in PERSONAL_CONTEXT_PATTERNS)


class AnswerCache:
    """Small in-memory TTL cache for AI answers, to conserve the shared free-tier quota.

    Keys are normalised public questions; nothing is written to disk.
    """

    def __init__(self, max_entries: int = 256, ttl: timedelta = timedelta(hours=12)) -> None:
        self._lock = Lock()
        self._entries: dict[tuple[str, str], tuple[datetime, AskResponse]] = {}
        self._max = max_entries
        self._ttl = ttl

    @staticmethod
    def key(question: str, language: str) -> tuple[str, str]:
        return (" ".join(question.casefold().split()), language)

    def get(self, question: str, language: str) -> AskResponse | None:
        now = datetime.now(UTC)
        with self._lock:
            entry = self._entries.get(self.key(question, language))
            if not entry or entry[0] < now:
                return None
            return entry[1]

    def put(self, question: str, language: str, response: AskResponse) -> None:
        now = datetime.now(UTC)
        with self._lock:
            if len(self._entries) >= self._max:
                self._entries = {k: v for k, v in self._entries.items() if v[0] >= now}
                while len(self._entries) >= self._max:
                    self._entries.pop(next(iter(self._entries)))
            self._entries[self.key(question, language)] = (now + self._ttl, response)


def _citations(hits: list[tuple[object, float]]) -> list[Citation]:
    citations = []
    for source, _score in hits:
        data = public_source(source)  # type: ignore[arg-type]
        citations.append(Citation(**data))
    return citations


def answer_question(question: str, language: str, provider: GeminiProvider, budget: RequestBudget,
                    per_minute: int, per_day: int, cache: AnswerCache | None = None) -> AskResponse:
    response = _answer(question, language, provider, budget, per_minute, per_day, cache)
    if contains_sensitive_details(question):
        return response
    # Change notices (renames, rate revisions) sit beside the answer, never inside it.
    notices = [ChangeNotice(**public_change(change, language)) for change in matching_changes(question)]
    return response.model_copy(update={"notices": notices}) if notices else response


def _answer(question: str, language: str, provider: GeminiProvider, budget: RequestBudget,
            per_minute: int, per_day: int, cache: AnswerCache | None) -> AskResponse:
    warning = TA_WARNING if language == "ta" else WARNING
    if mentions_personal_context(question):
        warning += TA_CONTEXT_NOTE if language == "ta" else CONTEXT_NOTE
    privacy_response = TA_PRIVACY_RESPONSE if language == "ta" else PRIVACY_RESPONSE
    no_evidence = TA_NO_EVIDENCE if language == "ta" else NO_EVIDENCE
    if contains_sensitive_details(question):
        return AskResponse(text=privacy_response, citations=[], mode="search", warning=warning)
    hits = retrieve(question, provider, limit=4)
    citations = _citations(hits)
    if not hits:
        return AskResponse(text=no_evidence, citations=[], mode="search", warning=warning)
    if not provider.available:
        return AskResponse(text=no_evidence, citations=citations, mode="search", warning=warning)
    if cache is not None:
        cached = cache.get(question, language)
        if cached is not None:
            return cached.model_copy(update={"warning": warning})
    if not budget.allow(per_minute, per_day):
        return AskResponse(text=no_evidence, citations=citations, mode="search", warning=warning)

    evidence = []
    for source, _score in hits:
        evidence.append({
            "id": source.id,
            "owner": source.owner,
            "title": source.title,
            "locator": source.locator,
            "text": source.text_ta if language == "ta" else source.text_en,
        })
    try:
        generated = provider.generate(question, language, evidence)
    except ProviderFailure as error:
        # Never return the provider message, request URL, or key to the client.
        reason = "quota or rate limit" if error.status == 429 else "provider unavailable"
        if language == "ta":
            reason = "பயன்பாட்டு வரம்பு" if error.status == 429 else "AI சேவை தற்காலிகமாகக் கிடைக்கவில்லை"
            outage = f" {reason}."
        else:
            outage = f" AI explanation is temporarily unavailable ({reason})."
        return AskResponse(
            text=f"{no_evidence}{outage}",
            citations=citations,
            mode="search",
            warning=warning,
        )

    if generated.unable_to_answer or not generated.claims:
        return AskResponse(text=no_evidence, citations=citations, mode="search", warning=warning)
    valid_ids = {source.id for source, _score in hits}
    evidence_by_id = {source.id: (source.title, source.text_en, source.text_ta) for source, _score in hits}
    used_ids: set[str] = set()
    valid_claims = []
    for claim in generated.claims:
        claim_ids = [item for item in claim.citation_ids if item in valid_ids]
        cited_text = [part for item in claim_ids for part in evidence_by_id[item]]
        if (claim.text.strip() and claim_ids and len(claim.text) <= 700
                and claim_is_supported(claim.text, cited_text)):
            valid_claims.append(claim.text.strip())
            used_ids.update(claim_ids)
    if not valid_claims:
        return AskResponse(text=no_evidence, citations=citations, mode="search", warning=warning)
    verified_citations = [citation for citation in citations if citation.id in used_ids]
    response = AskResponse(
        text="\n\n".join(valid_claims),
        citations=verified_citations,
        mode="ai",
        warning=warning,
    )
    if cache is not None:
        cache.put(question, language, response)
    return response
