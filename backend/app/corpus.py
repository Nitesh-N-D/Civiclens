"""Small public-source discovery corpus. Entries are not approved eligibility rules."""

from dataclasses import dataclass


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


SOURCES: tuple[SourceChunk, ...] = (
    SourceChunk(
        id="myscheme-pudhumai-penn",
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
        title="Social Security Schemes · Tamil Nadu CRA",
        url="https://cra.tn.gov.in/about_schemes_t.php",
        owner="Commissionerate of Revenue Administration and Disaster Management, Tamil Nadu",
        locator="Tamil scheme overview",
        status="Official overview · dates may be stale; do not rely on amounts",
        text_en=(
            "Tamil Nadu's Commissionerate of Revenue Administration lists social-security pension "
            "program categories including older adults, widows, persons with disabilities, agricultural "
            "workers, and other groups. The page also contains monetary and eligibility details tied to "
            "dated policy periods. CivicLens treats this page as a discovery lead only; current amounts "
            "and criteria are not verified."
        ),
        text_ta=(
            "வருவாய் நிர்வாக ஆணையரகத்தின் திட்டப் பக்கத்தில் முதியோர், விதவைகள், மாற்றுத் திறனாளிகள், "
            "விவசாயத் தொழிலாளர்கள் உள்ளிட்டோருக்கான சமூகப் பாதுகாப்பு ஓய்வூதியத் திட்ட வகைகள் "
            "பட்டியலிடப்பட்டுள்ளன. பக்கத்தில் காலவரையறை கொண்ட தொகை மற்றும் தகுதி விவரங்களும் "
            "உள்ளன. CivicLens இதைத் தகவல் கண்டறியும் ஆதாரமாக மட்டுமே கருதுகிறது; தற்போதைய "
            "தொகைகளும் விதிகளும் உறுதிப்படுத்தப்படவில்லை."
        ),
    ),
)


def public_source(chunk: SourceChunk) -> dict[str, str]:
    return {
        "id": chunk.id,
        "title": chunk.title,
        "url": chunk.url,
        "owner": chunk.owner,
        "locator": chunk.locator,
        "status": chunk.status,
    }
