"""Validators shared across services."""

from django.core.validators import RegexValidator

AREA_CODE_REGEX = r"^\d{3}$"
PHONE_NUMBER_REGEX = r"^\d{7}$"

area_code_validator = RegexValidator(
    regex=AREA_CODE_REGEX,
    message="Area code must be exactly three digits.",
)

phone_number_validator = RegexValidator(
    regex=PHONE_NUMBER_REGEX,
    message="Phone number must be exactly seven digits.",
)

__all__ = [
    "area_code_validator",
    "phone_number_validator",
    "AREA_CODE_REGEX",
    "PHONE_NUMBER_REGEX",
]
