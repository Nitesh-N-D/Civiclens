"""Deterministic eligibility screening, document checklists and application guidance.

Every criterion is a condition stated in the cited source's own text (see corpus.SOURCES); none is
invented here. Rules are evaluated by code, never by Gemini, and no answer is stored or logged.
Because no criterion has been human-verified against a current Government Order, the strongest
possible outcome is "requires_official_verification", never a guarantee of eligibility.

Profile answers are coarse, voluntary choices (no names, numbers, IDs or exact income).
"""

from dataclasses import dataclass
from typing import Literal

Outcome = Literal["met", "not_met", "unknown"]
Overall = Literal["appears_eligible", "appears_ineligible", "insufficient_information",
                  "requires_official_verification"]

# Allowed answers per profile field. "" (or a missing field) means "prefer not to say".
PROFILE_FIELDS: dict[str, tuple[str, ...]] = {
    "state": ("tamil_nadu", "other"),
    "education": ("school", "diploma", "undergraduate", "postgraduate", "not_studying"),
    "school_type": ("tn_government", "other"),
    "gender": ("female", "male", "other"),
    "community": ("bc", "mbc", "dnc", "other"),
    "college_type": ("government", "government_aided", "private", "not_applicable"),
}

FIELD_PURPOSE = {
    "state": ("Both schemes are Tamil Nadu schemes.", "இரு திட்டங்களும் தமிழ்நாட்டுத் திட்டங்கள்."),
    "education": ("Both schemes are for students in higher education.", "இரு திட்டங்களும் உயர்கல்வி மாணவர்களுக்கானவை."),
    "school_type": ("Pudhumai Penn's summary refers to Tamil Nadu government schools.", "புதுமைப் பெண் சுருக்கம் தமிழ்நாடு அரசுப் பள்ளிகளைக் குறிப்பிடுகிறது."),
    "gender": ("Pudhumai Penn's summary refers to girl students.", "புதுமைப் பெண் சுருக்கம் மாணவிகளைக் குறிப்பிடுகிறது."),
    "community": ("The Free Education Scheme summary refers to BC, MBC and DNC students.", "இலவசக் கல்வித் திட்டச் சுருக்கம் BC, MBC, DNC மாணவர்களைக் குறிப்பிடுகிறது."),
    "college_type": ("The Free Education Scheme summary refers to government and government-aided colleges.", "இலவசக் கல்வித் திட்டச் சுருக்கம் அரசு மற்றும் அரசு உதவிபெறும் கல்லூரிகளைக் குறிப்பிடுகிறது."),
}


@dataclass(frozen=True)
class Criterion:
    id: str
    field: str
    accepted: frozenset[str]
    label_en: str
    label_ta: str
    source_id: str
    # The phrase in the source text that states this condition (shown as evidence).
    basis: str
    human_verified: bool = False


@dataclass(frozen=True)
class DocumentItem:
    name_en: str
    name_ta: str
    reason_en: str
    reason_ta: str
    criterion_id: str
    source_id: str
    # The sources do not name specific documents; never present one as mandatory.
    verification: Literal["named_by_source", "not_named_by_source"] = "not_named_by_source"


@dataclass(frozen=True)
class Guidance:
    route_en: str
    route_ta: str
    steps_en: tuple[str, ...]
    steps_ta: tuple[str, ...]
    contact_en: str
    contact_ta: str
    source_id: str


CRITERIA: dict[str, tuple[Criterion, ...]] = {
    "pudhumai-penn": (
        Criterion("pp-state", "state", frozenset({"tamil_nadu"}), "Studying in Tamil Nadu",
                  "தமிழ்நாட்டில் படிப்பவர்", "myscheme-pudhumai-penn", "a Tamil Nadu higher-education assistance scheme"),
        Criterion("pp-gender", "gender", frozenset({"female"}), "Girl student", "மாணவி",
                  "myscheme-pudhumai-penn", "eligible girl students"),
        Criterion("pp-school", "school_type", frozenset({"tn_government"}),
                  "Studied in a Tamil Nadu government school", "தமிழ்நாடு அரசுப் பள்ளியில் படித்தவர்",
                  "myscheme-pudhumai-penn", "who studied in Tamil Nadu government schools"),
        Criterion("pp-course", "education", frozenset({"diploma", "undergraduate", "postgraduate"}),
                  "Pursuing a recognised higher-education course", "அங்கீகரிக்கப்பட்ட உயர்கல்விப் படிப்பில் சேர்ந்தவர்",
                  "myscheme-pudhumai-penn", "pursue a recognized higher-education course"),
    ),
    "free-education-tn": (
        Criterion("fe-state", "state", frozenset({"tamil_nadu"}), "Studying in Tamil Nadu",
                  "தமிழ்நாட்டில் படிப்பவர்", "myscheme-free-education-tn", "a Tamil Nadu Free Education Scheme"),
        Criterion("fe-community", "community", frozenset({"bc", "mbc", "dnc"}),
                  "From a Backward Class, Most Backward Class or Denotified Community",
                  "பிற்படுத்தப்பட்டோர், மிகவும் பிற்படுத்தப்பட்டோர் அல்லது சீர்மரபினர் சமூகத்தைச் சேர்ந்தவர்",
                  "myscheme-free-education-tn", "Backward Classes, Most Backward Classes, and Denotified Communities"),
        Criterion("fe-course", "education", frozenset({"undergraduate"}), "In an undergraduate programme",
                  "இளங்கலைப் படிப்பில் உள்ளவர்", "myscheme-free-education-tn", "certain undergraduate programs"),
        Criterion("fe-college", "college_type", frozenset({"government", "government_aided"}),
                  "At a government or government-aided arts and science college",
                  "அரசு அல்லது அரசு உதவிபெறும் கலை, அறிவியல் கல்லூரியில் படிப்பவர்",
                  "myscheme-free-education-tn", "government and government-aided arts and science colleges"),
    ),
}

DOCUMENTS: dict[str, tuple[DocumentItem, ...]] = {
    "pudhumai-penn": (
        DocumentItem("Proof of schooling in a Tamil Nadu government school", "தமிழ்நாடு அரசுப் பள்ளியில் படித்ததற்கான சான்று",
                     "The summary limits the scheme to students from Tamil Nadu government schools.",
                     "அரசுப் பள்ளி மாணவிகளுக்கே திட்டம் என சுருக்கம் கூறுகிறது.", "pp-school", "myscheme-pudhumai-penn"),
        DocumentItem("Proof of admission to a recognised higher-education course", "அங்கீகரிக்கப்பட்ட உயர்கல்விச் சேர்க்கைச் சான்று",
                     "The summary requires enrolment in a recognised higher-education course.",
                     "அங்கீகரிக்கப்பட்ட உயர்கல்விப் படிப்பில் சேர வேண்டும் என சுருக்கம் கூறுகிறது.", "pp-course", "myscheme-pudhumai-penn"),
    ),
    "free-education-tn": (
        DocumentItem("Community certificate (BC, MBC or DNC)", "சாதிச் சான்றிதழ் (BC, MBC அல்லது DNC)",
                     "The summary limits the scheme to BC, MBC and DNC students.",
                     "BC, MBC, DNC மாணவர்களுக்கே திட்டம் என சுருக்கம் கூறுகிறது.", "fe-community", "myscheme-free-education-tn"),
        DocumentItem("Proof of admission to an undergraduate programme at a government or aided college",
                     "அரசு/அரசு உதவிபெறும் கல்லூரியில் இளங்கலைச் சேர்க்கைச் சான்று",
                     "The summary covers certain undergraduate programmes at those colleges.",
                     "அக்கல்லூரிகளில் குறிப்பிட்ட இளங்கலைப் படிப்புகளுக்கே திட்டம் என சுருக்கம் கூறுகிறது.", "fe-college", "myscheme-free-education-tn"),
    ),
}

GUIDANCE: dict[str, Guidance] = {
    "pudhumai-penn": Guidance(
        "The myScheme summary names the Penkalvi portal as the application route.",
        "விண்ணப்ப வழியாக Penkalvi தளத்தை myScheme சுருக்கம் குறிப்பிடுகிறது.",
        ("Open the official myScheme page linked below and read the current rules.",
         "Confirm with your college or the Social Welfare and Women Empowerment Department that the scheme is open.",
         "Apply only through the official route the department names; CivicLens does not take applications."),
        ("கீழே உள்ள அதிகாரப்பூர்வ myScheme பக்கத்தில் தற்போதைய விதிகளைப் படிக்கவும்.",
         "திட்டம் நடப்பில் உள்ளதா என உங்கள் கல்லூரி அல்லது சமூகநலம் மற்றும் மகளிர் உரிமைத்துறையிடம் உறுதிப்படுத்தவும்.",
         "துறை குறிப்பிடும் அதிகாரப்பூர்வ வழியில் மட்டுமே விண்ணப்பிக்கவும்; CivicLens விண்ணப்பங்களைப் பெறுவதில்லை."),
        "Social Welfare and Women Empowerment Department, Tamil Nadu (or your college's scholarship desk)",
        "சமூகநலம் மற்றும் மகளிர் உரிமைத்துறை, தமிழ்நாடு (அல்லது உங்கள் கல்லூரி உதவித்தொகைப் பிரிவு)",
        "myscheme-pudhumai-penn",
    ),
    "free-education-tn": Guidance(
        "The summary does not name an application route.",
        "சுருக்கம் விண்ணப்ப வழியைக் குறிப்பிடவில்லை.",
        ("Open the official myScheme page linked below; it refers to an older launch date.",
         "Ask your college office or the BC, MBC and Minorities Welfare Department for the current order and how to apply.",
         "Keep copies of what you submit; CivicLens does not take applications."),
        ("கீழே உள்ள அதிகாரப்பூர்வ myScheme பக்கத்தைத் திறக்கவும்; அதில் பழைய தொடக்கத் தேதி உள்ளது.",
         "தற்போதைய அரசாணை மற்றும் விண்ணப்ப முறையை உங்கள் கல்லூரி அலுவலகம் அல்லது BC, MBC மற்றும் சிறுபான்மையினர் நலத்துறையிடம் கேட்கவும்.",
         "நீங்கள் சமர்ப்பிப்பவற்றின் நகல்களை வைத்திருக்கவும்; CivicLens விண்ணப்பங்களைப் பெறுவதில்லை."),
        "Backward Classes, Most Backward Classes and Minorities Welfare Department, Tamil Nadu",
        "பிற்படுத்தப்பட்டோர், மிகவும் பிற்படுத்தப்பட்டோர் மற்றும் சிறுபான்மையினர் நலத்துறை, தமிழ்நாடு",
        "myscheme-free-education-tn",
    ),
}


def clean_profile(profile: dict[str, str]) -> dict[str, str]:
    """Keep only known fields with allowed values; anything else counts as unanswered."""
    return {k: v for k, v in profile.items() if k in PROFILE_FIELDS and v in PROFILE_FIELDS[k]}


def evaluate_criterion(criterion: Criterion, profile: dict[str, str]) -> Outcome:
    value = profile.get(criterion.field)
    if value is None:
        return "unknown"
    return "met" if value in criterion.accepted else "not_met"


def overall(outcomes: list[Outcome], verified: bool) -> Overall:
    if "not_met" in outcomes:
        return "appears_ineligible"
    if "unknown" in outcomes:
        return "insufficient_information"
    return "appears_eligible" if verified else "requires_official_verification"


def assess(scheme_id: str, profile: dict[str, str], language: str) -> dict:
    """One scheme's screening result, documents and guidance. Raises KeyError for unknown schemes."""
    criteria = CRITERIA[scheme_id]
    profile = clean_profile(profile)
    ta = language == "ta"
    rows, outcomes = [], []
    for criterion in criteria:
        outcome = evaluate_criterion(criterion, profile)
        outcomes.append(outcome)
        rows.append({
            "id": criterion.id,
            "label": criterion.label_ta if ta else criterion.label_en,
            "field": criterion.field,
            "outcome": outcome,
            "source_id": criterion.source_id,
            "basis": criterion.basis,
            "human_verified": criterion.human_verified,
        })
    status = overall(outcomes, all(c.human_verified for c in criteria))
    met = {row["id"] for row in rows if row["outcome"] != "not_met"}
    guide = GUIDANCE[scheme_id]
    return {
        "scheme_id": scheme_id,
        "status": status,
        "criteria": rows,
        "missing_fields": sorted({row["field"] for row in rows if row["outcome"] == "unknown"}),
        "documents": [
            {
                "name": d.name_ta if ta else d.name_en,
                "reason": d.reason_ta if ta else d.reason_en,
                "criterion_id": d.criterion_id,
                "source_id": d.source_id,
                "mandatory": False,  # no source establishes a specific mandatory document yet
                "verification": d.verification,
            }
            for d in DOCUMENTS.get(scheme_id, ())
            if d.criterion_id in met
        ],
        "guidance": {
            "route": guide.route_ta if ta else guide.route_en,
            "steps": list(guide.steps_ta if ta else guide.steps_en),
            "contact": guide.contact_ta if ta else guide.contact_en,
            "source_id": guide.source_id,
        },
    }


def questions(language: str) -> list[dict]:
    """The voluntary questions, each with why it is asked."""
    ta = language == "ta"
    return [
        {"field": field, "options": list(options), "purpose": FIELD_PURPOSE[field][1 if ta else 0]}
        for field, options in PROFILE_FIELDS.items()
    ]


def compare_rows(scheme_ids: list[str], language: str) -> list[dict]:
    """Side-by-side criteria and routes; every cell names the source it came from."""
    ta = language == "ta"
    return [
        {
            "scheme_id": scheme_id,
            "criteria": [c.label_ta if ta else c.label_en for c in CRITERIA[scheme_id]],
            "documents": [d.name_ta if ta else d.name_en for d in DOCUMENTS.get(scheme_id, ())],
            "route": GUIDANCE[scheme_id].route_ta if ta else GUIDANCE[scheme_id].route_en,
            "contact": GUIDANCE[scheme_id].contact_ta if ta else GUIDANCE[scheme_id].contact_en,
            "source_id": GUIDANCE[scheme_id].source_id,
        }
        for scheme_id in scheme_ids
        if scheme_id in CRITERIA
    ]
