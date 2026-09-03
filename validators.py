"""
validators.py
--------------
Holds VALIDATION & EXTRACTION FUNCTIONS using Regular Expressions and type checking.
"""

import re
from datetime import datetime

from exceptions import (
    InvalidCurrencyError,
    InvalidAmountError,
    InvalidDurationError,
    InvalidDateError,
    InvalidCountryCodeError,
)

# Regular expressions for validation & extraction
CURRENCY_CODE_PATTERN = re.compile(r"^[A-Z]{3}$")
COUNTRY_CODE_PATTERN = re.compile(r"^[A-Z]{2}$")
PRICE_REGEX = re.compile(r"[\d,]+(?:\.\d+)?")


def validate_currency_code(code):
    """
    Check that the code looks like a real 3-letter currency code (e.g. USD, NGN, GBP).
    Strips extra spaces and converts to uppercase.
    """
    if not code or not isinstance(code, str):
        raise InvalidCurrencyError(f"Currency code must be text, got: {code!r}")
    cleaned = code.strip().upper()

    if not CURRENCY_CODE_PATTERN.match(cleaned):
        raise InvalidCurrencyError(
            f"'{code}' is not a valid currency code. "
            "Currency codes must be exactly 3 letters (e.g. USD, NGN, GBP)."
        )

    return cleaned


def validate_country_code(code):
    """Check that the code looks like a real 2-letter country code (e.g. NG, US, GB)."""
    if not code or not isinstance(code, str):
        raise InvalidCountryCodeError(f"Country code must be text, got: {code!r}")

    cleaned = code.strip().upper()

    if not COUNTRY_CODE_PATTERN.match(cleaned):
        raise InvalidCountryCodeError(
            f"'{code}' is not a valid country code. "
            "Country codes must be 2 letters (e.g. NG, US, GB)."
        )
    return cleaned


def extract_price_from_text(text):
    """
    Extract a numeric price from user input string using regular expressions.
    Example: '$150.50' -> 150.50, '50,000 NGN' -> 50000.0
    """
    if not text:
        return 0.0
    match = PRICE_REGEX.search(str(text))
    if not match:
        raise InvalidAmountError(f"Could not extract a valid price from input: {text!r}")
    raw_str = match.group(0).replace(",", "")
    return float(raw_str)


def validate_amount(amount, field_name="amount"):
    """
    Check that amount is a positive number (int/float or numeric text like '$50').
    Returns the amount as a float.
    """
    try:
        if isinstance(amount, str) and not amount.replace(".", "", 1).isdigit():
            value = extract_price_from_text(amount)
        else:
            value = float(amount)
    except (TypeError, ValueError):
        raise InvalidAmountError(f"{field_name} must be a number, got: {amount!r}")

    if value < 0:
        raise InvalidAmountError(f"{field_name} cannot be negative, got: {value}")

    return value


def validate_duration(days):
    """Check that `days` is a positive whole number of days."""
    try:
        value = int(days)
    except (TypeError, ValueError):
        raise InvalidDurationError(f"Trip duration must be a whole number, got: {days!r}")

    if value <= 0:
        raise InvalidDurationError(f"Trip duration must be at least 1 day, got: {value}")

    return value


def validate_date(date_str, field_name="date"):
    """Check that `date_str` is a real date in YYYY-MM-DD format."""
    if not date_str:
        raise InvalidDateError(f"{field_name} is required.")

    try:
        return datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise InvalidDateError(
            f"'{date_str}' is not a valid {field_name}. "
            "Use the format YYYY-MM-DD, e.g. '2026-12-25'."
        )


def validate_date_range(start_date_str, end_date_str):
    start = validate_date(start_date_str, field_name="start date")
    end = validate_date(end_date_str, field_name="end date")

    if end < start:
        raise InvalidDateError(
            f"End date ({end}) cannot be before start date ({start})."
        )
    return start, end