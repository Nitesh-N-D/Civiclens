"""Tokenisation shared by retrieval, change matching and answer validation (EN + TA)."""

import re

TOKEN_RE = re.compile(r"[\w஀-௿]+", re.UNICODE)

PREFIX_MIN_LENGTH = 5

# Function words and words that occur in almost every Tamil Nadu scheme query,
# which on their own say nothing about relevance.
STOPWORDS = frozenset(
    """a an the is are was were be been am im me my we our us you your he she it its they them their this that
    these those of in on at to for from by with and or not no do does did can could will would should may might
    what which who whom whose when where why how any some all there here get got give need want about also
    tamil nadu tn government govt scheme schemes current please tell know available apply""".split()
) | frozenset(
    "நான் என் எனது எனக்கு எங்கள் நாங்கள் என்ன எப்படி எங்கே எந்த யார் ஏதாவது உள்ளது உண்டா ஒரு மற்றும் "
    "தமிழ்நாடு தமிழ்நாட்டின் தமிழ்நாட்டில் அரசு திட்டம் திட்டங்கள் கிடைக்கும் வேண்டும் பற்றி இருக்கிறதா".split()
)


def _stem(token: str) -> str:
    # Light English plural folding; applied identically to queries and documents.
    if token.isascii() and len(token) > 4:
        if token.endswith("ies"):
            return token[:-3] + "y"
        if token.endswith("es") and token[-3] in "sxz":
            return token[:-2]
        if token.endswith("s") and not token.endswith("ss"):
            return token[:-1]
    return token


def tokens(text: str) -> list[str]:
    return [_stem(token.casefold()) for token in TOKEN_RE.findall(text) if len(token) > 1]


def query_tokens(text: str) -> list[str]:
    return [token for token in tokens(text) if token not in STOPWORDS]


def matches(query_token: str, doc_token: str) -> bool:
    if query_token == doc_token:
        return True
    # Prefix match handles Tamil case suffixes (கல்லூரி / கல்லூரியில்) and English
    # inflection (scholarship / scholarships) without a morphology library.
    shorter, longer = sorted((query_token, doc_token), key=len)
    return len(shorter) >= PREFIX_MIN_LENGTH and longer.startswith(shorter)
