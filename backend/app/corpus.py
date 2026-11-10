"""Small public-source discovery corpus. Entries are not approved eligibility rules."""

from dataclasses import dataclass
from typing import Any

from .models import SchemeCard


@dataclass(frozen=True)
class SourceChunk:
    id: str
    title: str
    url: str
    owner: str
    locator: str
    status: str
    text_en: str
    text_ta: str
    # TD-04 freshness re-check against 2026 sources: 10 Nov 2026.
    desk_checked_at: str = "2026-11-10"
    human_verified_at: str | None = None
    # Curated search aliases (EN + TA). Used for retrieval only; never shown as evidence.
    keywords: str = ""


SOURCES: tuple[SourceChunk, ...] = (
    SourceChunk(
        id="myscheme-pudhumai-penn",
        keywords="puthumai pudhumaipenn moovalur ramamirtham ammaiyar penkalvi monthly 1000 scholarship assistance girl women female college degree diploma higher education government school உதவித்தொகை மாணவி பெண் கல்லூரி உயர்கல்வி பள்ளி புதுமை மூவலூர் இராமாமிர்தம் அம்மையார்",
        title="Moovalur Ramamirtham Ammaiyar Higher Education Assurance Scheme (Pudhumai Penn)",
        url="https://www.myscheme.gov.in/schemes/pudhumai-penn-scheme",
        owner="myScheme · Digital India Corporation, MeitY",
        locator="Scheme overview and FAQ",
        status="Official directory · confirm current rules with Tamil Nadu",
        text_en=(
            "myScheme describes Pudhumai Penn as a Tamil Nadu higher-education assistance scheme. "
            "Its overview says assistance is for eligible girl students who studied in Tamil Nadu "
            "government schools and pursue a recognized higher-education course. It names the "
            "Penkalvi portal as an application route. This is a directory summary, not a current "
            "controlling Government Order; current rules and application status require confirmation "
            "from the Tamil Nadu Social Welfare and Women Empowerment Department."
        ),
        text_ta=(
            "myScheme இணையதளம் புதுமைப் பெண் திட்டத்தை தமிழ்நாட்டின் உயர்கல்வி உதவித் திட்டமாக "
            "விவரிக்கிறது. தமிழ்நாடு அரசுப் பள்ளிகளில் படித்து, அங்கீகரிக்கப்பட்ட உயர்கல்விப் "
            "படிப்பில் சேரும் தகுதியுள்ள மாணவிகளுக்கான உதவி என அதன் சுருக்கம் கூறுகிறது; விண்ணப்ப "
            "வழியாக Penkalvi தளத்தைக் குறிப்பிடுகிறது. இது திட்டக் கோப்பகச் சுருக்கம் மட்டுமே; "
            "தற்போதைய விதிகள் மற்றும் விண்ணப்ப நிலையைத் தமிழ்நாடு சமூகநலம் மற்றும் மகளிர் "
            "உரிமைத்துறை மூலம் உறுதிப்படுத்த வேண்டும்."
        ),
    ),
    SourceChunk(
        id="myscheme-free-education-tn",
        keywords="free education scheme FES special fee compulsory fee polytechnic scholarship fee waiver tuition college degree undergraduate backward class BC MBC DNC denotified community உதவித்தொகை கட்டணம் கல்லூரி பிற்படுத்தப்பட்டோர் சீர்மரபினர் இலவசக் கல்வி சிறப்புக் கட்டணம்",
        title="Free Education Scheme · Tamil Nadu",
        url="https://www.myscheme.gov.in/schemes/fes",
        owner="myScheme · Digital India Corporation, MeitY",
        locator="Scheme overview",
        status="Official directory · confirm current rules with Tamil Nadu",
        text_en=(
            "myScheme describes a Tamil Nadu Free Education Scheme for students from Backward "
            "Classes, Most Backward Classes, and Denotified Communities in certain undergraduate "
            "programs at government and government-aided arts and science colleges. The overview "
            "says covered fees are paid as prescribed by government. The scheme page refers to an "
            "older launch date, so eligibility, covered programs, fee amounts, and application steps "
            "must be confirmed against current orders from the BC, MBC and Minorities Welfare Department."
        ),
        text_ta=(
            "BC, MBC மற்றும் சீர்மரபினர் சமூக மாணவர்களுக்கான தமிழ்நாடு இலவசக் கல்வித் திட்டம் "
            "பற்றி myScheme சுருக்கம் வழங்குகிறது. அரசு மற்றும் அரசு உதவிபெறும் கலை, அறிவியல் "
            "கல்லூரிகளில் குறிப்பிட்ட இளங்கலைப் படிப்புகளுக்கான கட்டண உதவியை அது குறிப்பிடுகிறது. "
            "இணையதளத்தில் பழைய தொடக்கத் தேதி குறிப்பிடப்பட்டுள்ளதால், தற்போதைய தகுதி, படிப்புகள், "
            "தொகை மற்றும் விண்ணப்ப முறையை BC, MBC மற்றும் சிறுபான்மையினர் நலத்துறையின் சமீபத்திய "
            "அரசாணைகளில் உறுதிப்படுத்த வேண்டும்."
        ),
    ),
    SourceChunk(
        id="tnesevai-service-list",
        keywords="certificate income community nativity caste e-Sevai esevai centre center apply application documents சான்றிதழ் வருமானச் சாதிச் இ-சேவை மையம் விண்ணப்பம் ஆவணங்கள்",
        title="Tamil Nadu e-Sevai · Service list",
        url="https://www.tnesevai.tn.gov.in/Pages/ServiceList.aspx",
        owner="Tamil Nadu e-Governance Agency (TNeGA)",
        locator="Public service directory",
        status="Official service directory · verify service-specific instructions",
        text_en=(
            "Tamil Nadu e-Sevai publishes a service list covering services from multiple departments. "
            "The public list includes application routes for certificates and social-security services. "
            "The documents shown for an individual service are process information and do not establish "
            "that a person qualifies for a scheme. Confirm requirements on the live service page or at "
            "an authorized e-Sevai center."
        ),
        text_ta=(
            "தமிழ்நாடு e-Sevai பல துறைகளின் சேவைகளைப் பட்டியலிடுகிறது. சான்றிதழ்கள் மற்றும் "
            "சமூகப் பாதுகாப்புச் சேவைகளுக்கான விண்ணப்ப வழிகளும் பட்டியலில் உள்ளன. ஒவ்வொரு "
            "சேவைக்கும் காட்டப்படும் ஆவணங்கள் விண்ணப்ப நடைமுறைத் தகவல் மட்டுமே; ஒருவருக்குத் "
            "திட்டத் தகுதி உண்டு என்பதை அவை நிரூபிக்காது. நேரடி சேவைப் பக்கம் அல்லது அங்கீகரிக்கப்பட்ட "
            "e-Sevai மையத்தில் தேவைகளை உறுதிப்படுத்தவும்."
        ),
    ),
    SourceChunk(
        id="cra-social-security-overview",
        keywords="pension OAP IGNOAPS IGNWPS IGNDPS NSAP uzhavar pathukappu destitute deserted unmarried women 1200 1500 monthly amount pension old age elderly senior citizen widow destitute disability disabled differently abled agricultural labourer ஓய்வூதியம் முதியோர் விதவை கைம்பெண் மாற்றுத்திறனாளி விவசாயத் தொழிலாளர் உழவர் பாதுகாப்பு ஆதரவற்ற தொகை",
        title="Social Security Schemes · Tamil Nadu CRA",
        url="https://cra.tn.gov.in/about_schemes_t.php",
        owner="Commissionerate of Revenue Administration and Disaster Management, Tamil Nadu",
        locator="Tamil scheme overview",
        status="Official overview · amounts dated 2023; confirm current figures with the Taluk office",
        text_en=(
            "Tamil Nadu's Commissionerate of Revenue Administration lists social-security pension "
            "program categories including older adults, widows, persons with disabilities, agricultural "
            "workers, and other groups. As checked on 10 November 2026, the page states that the "
            "disability pension was raised to Rs 1,500 a month from 1 January 2023 and the other "
            "social-security pensions to Rs 1,200 a month from August 2023, and that applications are "
            "made through Tamil Nadu e-Sevai. These figures are dated; CivicLens has not verified that "
            "they are current, and eligibility must be decided by the Revenue Department."
        ),
        text_ta=(
            "வருவாய் நிர்வாக ஆணையரகத்தின் திட்டப் பக்கத்தில் முதியோர், விதவைகள், மாற்றுத் திறனாளிகள், "
            "விவசாயத் தொழிலாளர்கள் உள்ளிட்டோருக்கான சமூகப் பாதுகாப்பு ஓய்வூதியத் திட்ட வகைகள் "
            "பட்டியலிடப்பட்டுள்ளன. 10 நவம்பர் 2026 அன்று பார்த்தபோது, மாற்றுத் திறனாளிகள் ஓய்வூதியம் "
            "01.01.2023 முதல் மாதம் ரூ.1,500 ஆகவும், பிற சமூகப் பாதுகாப்பு ஓய்வூதியங்கள் ஆகஸ்டு 2023 "
            "முதல் மாதம் ரூ.1,200 ஆகவும் உயர்த்தப்பட்டதாகவும், விண்ணப்பங்கள் தமிழ்நாடு e-Sevai மூலம் "
            "செய்யப்படுவதாகவும் பக்கம் கூறுகிறது. இவை பழைய தேதியிட்ட தொகைகள்; இவை தற்போதையவை என "
            "CivicLens உறுதிப்படுத்தவில்லை; தகுதியை வருவாய்த் துறையே தீர்மானிக்கும்."
        ),
    ),
)

SCHEMES: dict[str, dict[str, Any]] = {
    "pudhumai-penn": {
        "title_en": "Pudhumai Penn",
        "title_ta": "புதுமைப் பெண்",
        "department_en": "Social Welfare and Women Empowerment Department, Tamil Nadu",
        "department_ta": "சமூகநலம் மற்றும் மகளிர் உரிமைத்துறை, தமிழ்நாடு",
        "category_en": "Higher education",
        "category_ta": "உயர்கல்வி",
        "overview_en": "An education-support scheme listed by myScheme. Current eligibility and application status have not been verified against the latest department rules.",
        "overview_ta": "myScheme-இல் பட்டியலிடப்பட்டுள்ள கல்வி உதவித் திட்டம். தற்போதைய தகுதியும் விண்ணப்ப நிலையும் சமீபத்திய துறை விதிகளுடன் ஒப்பிட்டு உறுதிப்படுத்தப்படவில்லை.",
        "source_id": "myscheme-pudhumai-penn",
    },
    "free-education-tn": {
        "title_en": "Free Education Scheme",
        "title_ta": "இலவசக் கல்வித் திட்டம்",
        "department_en": "Backward Classes, Most Backward Classes and Minorities Welfare Department, Tamil Nadu",
        "department_ta": "பிற்படுத்தப்பட்டோர், மிகவும் பிற்படுத்தப்பட்டோர் மற்றும் சிறுபான்மையினர் நலத்துறை, தமிழ்நாடு",
        "category_en": "Higher education",
        "category_ta": "உயர்கல்வி",
        "overview_en": "A Tamil Nadu higher-education fee-support scheme listed by myScheme. Current criteria and application steps have not been verified against current department orders.",
        "overview_ta": "myScheme-இல் பட்டியலிடப்பட்டுள்ள தமிழ்நாட்டின் உயர்கல்விக் கட்டண உதவித் திட்டம். தற்போதைய தகுதி மற்றும் விண்ணப்ப வழிமுறைகள் சமீபத்திய அரசாணைகளுடன் உறுதிப்படுத்தப்படவில்லை.",
        "source_id": "myscheme-free-education-tn",
    },
}


def public_source(chunk: SourceChunk) -> dict[str, str | None]:
    return {
        "id": chunk.id,
        "title": chunk.title,
        "url": chunk.url,
        "owner": chunk.owner,
        "locator": chunk.locator,
        "status": chunk.status,
        "desk_checked_at": chunk.desk_checked_at,
        "human_verified_at": chunk.human_verified_at,
    }


def public_schemes(language: str = "en") -> list[SchemeCard]:
    source_ids = {source.id for source in SOURCES}
    cards = []
    for scheme_id, record in SCHEMES.items():
        if record["source_id"] not in source_ids:
            continue
        is_tamil = language == "ta"
        source = next(source for source in SOURCES if source.id == record["source_id"])
        cards.append(SchemeCard(
            id=scheme_id,
            title=record["title_ta"] if is_tamil else record["title_en"],
            department=record["department_ta"] if is_tamil else record["department_en"],
            category=record["category_ta"] if is_tamil else record["category_en"],
            overview=record["overview_ta"] if is_tamil else record["overview_en"],
            url=source.url,
            source_id=source.id,
            status=("தகுதி விதிகள் சரிபார்க்கப்படவில்லை" if is_tamil else "Eligibility rules not verified"),
            eligibility_enabled=False,
        ))
    return cards
