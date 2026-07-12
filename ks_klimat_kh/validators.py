import re

from django.core.exceptions import ValidationError

PHONE_ALLOWED_RE = re.compile(r"^\+?[0-9][0-9()\-\s]{6,18}[0-9]$")
PHONE_DIGIT_RE = re.compile(r"\d")
REPEATED_PUNCTUATION_RE = re.compile(r"[\s()\-]{3,}")


def validate_phone(value):
    phone = (value or "").strip()
    digits = PHONE_DIGIT_RE.findall(phone)
    if (
        not PHONE_ALLOWED_RE.match(phone)
        or len(digits) < 7
        or len(digits) > 15
        or REPEATED_PUNCTUATION_RE.search(phone)
        or phone.count("+") > 1
        or ("+" in phone and not phone.startswith("+"))
    ):
        raise ValidationError("Invalid phone.")
    return phone
