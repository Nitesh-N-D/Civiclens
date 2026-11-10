"""Scheme change tracking: renames, continuations and rate revisions found in freshness checks.

These notices are shown beside answers, never used as answer evidence. Each one says whether
it comes from an official page or a news report, so a reported (unconfirmed) rename is never
presented as a government decision.
"""

from dataclasses import dataclass
from typing import Literal

from .retrieval import _matches, query_tokens


@dataclass(frozen=True)
class SchemeChange:
    id: str
    scheme_en: str
    scheme_ta: str
    # Names people may still use, old and new; matched against questions.
    names: tuple[str, ...]
    status: Literal["official", "reported"]
    summary_en: str
    summary_ta: str
    source_title: str
    source_url: str
    checked_at: str


CHANGES: tuple[SchemeChange, ...] = (
    SchemeChange(
        id="pudhumai-penn-continued-2026",
        scheme_en="Pudhumai Penn",
        scheme_ta="புதுமைப் பெண்",
        names=("pudhumai penn", "puthumai penn", "moovalur ramamirtham", "புதுமைப் பெண்", "புதுமை பெண்", "மூவலூர்"),
        status="reported",
        summary_en=(
            "News reports from May 2026 say the new Tamil Nadu government will continue Pudhumai Penn. "
            "CivicLens found no rename. This is a news report, not a Government Order."
        ),
        summary_ta=(
            "புதிய தமிழ்நாடு அரசு புதுமைப் பெண் திட்டத்தைத் தொடரும் என மே 2026 செய்திகள் கூறுகின்றன. "
            "பெயர் மாற்றம் எதுவும் காணப்படவில்லை. இது செய்தி அறிக்கை மட்டுமே; அரசாணை அல்ல."
        ),
        source_title="Oneindia news report (May 2026)",
        source_url="https://www.oneindia.com/chennai/pudhumai-penn-scheme-puthumai-penn-thittam-how-to-apply-online-details-inside-8087331.html",
        checked_at="2026-11-10",
    ),
    SchemeChange(
        id="magalir-urimai-rename-reported-2026",
        scheme_en="Kalaignar Magalir Urimai Thogai",
        scheme_ta="கலைஞர் மகளிர் உரிமைத் தொகை",
        names=("magalir urimai", "urimai thogai", "mathippumigu", "madhippumigu", "மகளிர் உரிமை", "உரிமைத் தொகை",
               "மதிப்புமிகு"),
        status="reported",
        summary_en=(
            "News reports say the government is considering renaming this scheme 'Mathippumigu Magalir Thittam' "
            "and changing the amount. No Government Order confirming this was found. CivicLens has no reviewed "
            "source for this scheme yet; check with the Social Welfare Department."
        ),
        summary_ta=(
            "இத்திட்டத்தை 'மதிப்புமிகு மகளிர் திட்டம்' என மறுபெயரிட்டு தொகையை மாற்ற அரசு பரிசீலிப்பதாகச் "
            "செய்திகள் கூறுகின்றன. இதை உறுதிப்படுத்தும் அரசாணை கிடைக்கவில்லை. இத்திட்டத்திற்கு CivicLens-இடம் "
            "சரிபார்க்கப்பட்ட ஆதாரம் இல்லை; சமூகநலத் துறையிடம் உறுதிப்படுத்தவும்."
        ),
        source_title="Oneindia news report (2026)",
        source_url="https://www.oneindia.com/chennai/magalir-urimai-thogai-update-tn-women-to-get-rs-1500-as-vijay-govt-set-to-hike-rs-500-in-first-phas-8093437.html",
        checked_at="2026-11-10",
    ),
    SchemeChange(
        id="social-security-pension-rates-2023",
        scheme_en="Social security pensions",
        scheme_ta="சமூகப் பாதுகாப்பு ஓய்வூதியங்கள்",
        names=("pension", "old age", "widow", "ஓய்வூதியம்", "முதியோர்", "விதவை", "கைம்பெண்"),
        status="official",
        summary_en=(
            "The Revenue Administration page states that the disability pension became Rs 1,500 a month from "
            "1 January 2023 and the other social security pensions Rs 1,200 a month from August 2023. CivicLens "
            "found no 2026 revision. Confirm the current amount with the Taluk office before relying on it."
        ),
        summary_ta=(
            "மாற்றுத் திறனாளிகள் ஓய்வூதியம் 01.01.2023 முதல் மாதம் ரூ.1,500 ஆகவும், பிற சமூகப் பாதுகாப்பு "
            "ஓய்வூதியங்கள் ஆகஸ்டு 2023 முதல் மாதம் ரூ.1,200 ஆகவும் உயர்த்தப்பட்டதாக வருவாய் நிர்வாகப் பக்கம் "
            "கூறுகிறது. 2026 மாற்றம் எதுவும் காணப்படவில்லை. தற்போதைய தொகையை வட்டாட்சியர் அலுவலகத்தில் உறுதிப்படுத்தவும்."
        ),
        source_title="Social Security Schemes · Tamil Nadu CRA",
        source_url="https://cra.tn.gov.in/about_schemes_t.php",
        checked_at="2026-11-10",
    ),
)


def _name_tokens(name: str) -> list[str]:
    # Keep scheme names whole: "old age" must not be reduced to stopword-filtered fragments.
    return query_tokens(name) or name.casefold().split()


def matching_changes(question: str) -> list[SchemeChange]:
    """Changes whose any name appears (all its tokens) in the question."""
    asked = query_tokens(question)
    found = []
    for change in CHANGES:
        for name in change.names:
            wanted = _name_tokens(name)
            if wanted and all(any(_matches(token, q) for q in asked) for token in wanted):
                found.append(change)
                break
    return found


def public_change(change: SchemeChange, language: str = "en") -> dict[str, str]:
    is_tamil = language == "ta"
    return {
        "id": change.id,
        "scheme": change.scheme_ta if is_tamil else change.scheme_en,
        "status": change.status,
        "summary": change.summary_ta if is_tamil else change.summary_en,
        "source_title": change.source_title,
        "source_url": change.source_url,
        "checked_at": change.checked_at,
    }
