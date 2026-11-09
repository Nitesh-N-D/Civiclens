import re
from datetime import datetime, timedelta, timezone
from threading import Lock

from .corpus import public_source
from .gemini import GeminiProvider, ProviderFailure
from .models import AskResponse, Citation
from .retrieval import retrieve

SENSITIVE_PATTERNS = (
    re.compile(r"\b(?:aadhaar|aadhar|uidai|pan card|passport|voter id|account number|ifsc|otp|password)\b", re.I),
    re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.I),
    re.compile(r"\b\d{12}\b"),
    re.compile(r"\b(?:\+?91[\s-]?)?[6-9]\d{9}\b"),
    re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", re.I),
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Z]{2,}\b", re.I),
    re.compile(r"\b(?:my|our)\s+(?:age|income|bank|account|aadhaar|aadhar|phone|address|disability|caste|community)\b", re.I),
    re.compile(r"\bI\s+am\s+(?:\d{1,3}|a\s+widow|disabled|pregnant)\b", re.I),
    re.compile(r"\b(?:I am|I'm|my age is)\s+(?:a\s+)?\d{1,3}\b", re.I),
    re.compile(r"(?:என் வயது|எனக்கு வயது)\s*[:=]?\s*[\d௦-௯]{1,3}"),
    re.compile(r"(?:என் ஆதார்|ஆதார் எண்|வங்கி கணக்கு எண்|என் வங்கிக் கணக்கு)"),
    re.compile(r"\b(?:I am|I'm)\s+(?:a\s+)?(?:student|farmer|widow|senior citizen|person with a disability)\b", re.I),
    re.compile(r"\bmy\s+(?:caste|community|disability|income|household|family)\b", re.I),
    re.compile(r"(?:நான்|என் குடும்பம்|எனது குடும்பம்|எங்கள் குடும்பம்)"),
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


class RequestBudget:
    def __init__(self) -> None:
        self._lock = Lock()
        self._minute: list[datetime] = []
        self._day = datetime.now(timezone.utc).date()
        self._daily = 0

    def allow(self, per_minute: int, per_day: int) -> bool:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=1)
        with self._lock:
            self._minute = [stamp for stamp in self._minute if stamp > cutoff]
            if self._day != now.date():
                self._day = now.date()
                self._daily = 0
            if len(self._minute) >= per_minute or self._daily >= per_day:
                return False
            self._minute.append(now)
            self._daily += 1
            return True


def contains_sensitive_details(text: str) -> bool:
    return any(pattern.search(text) for pattern in SENSITIVE_PATTERNS)


def _citations(hits: list[tuple[object, float]]) -> list[Citation]:
    citations = []
    for source, _score in hits:
        data = public_source(source)  # type: ignore[arg-type]
        citations.append(Citation(**data))
    return citations


def answer_question(question: str, language: str, provider: GeminiProvider, budget: RequestBudget,
                    per_minute: int, per_day: int) -> AskResponse:
    warning = TA_WARNING if language == "ta" else WARNING
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
    used_ids: set[str] = set()
    valid_claims = []
    for claim in generated.claims:
        claim_ids = [item for item in claim.citation_ids if item in valid_ids]
        if claim.text.strip() and claim_ids and len(claim.text) <= 700:
            valid_claims.append(claim.text.strip())
            used_ids.update(claim_ids)
    if not valid_claims:
        return AskResponse(text=no_evidence, citations=citations, mode="search", warning=warning)
    verified_citations = [citation for citation in citations if citation.id in used_ids]
    return AskResponse(
        text="\n\n".join(valid_claims),
        citations=verified_citations,
        mode="ai",
        warning=warning,
    )
