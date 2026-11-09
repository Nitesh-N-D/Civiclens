import hmac


def valid_bearer_token(expected: str, authorization: str | None) -> bool:
    if not expected or not authorization:
        return False
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].casefold() != "bearer":
        return False
    return hmac.compare_digest(parts[1].strip(), expected)
