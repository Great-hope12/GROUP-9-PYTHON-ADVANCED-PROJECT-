"""
Handles everything related to CURRENCY CONVERSION:
  like fetching live exchange rates from the ExchangeRate-API
  converting an amount from one currency to another
  raising clear errors when a currency code is bad, a rate is missing, or the API/network fails

API keys are managed by the developer via environment variables (.env file).
If no API key is set, the app automatically defaults to the free, keyless open rate API!
"""

import os
import requests

from exceptions import MissingDataError, APIError
from validators import validate_currency_code, validate_amount

# Standard API URL with key and Open/Free URL without key
EXCHANGE_RATE_API_URL = "https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
OPEN_EXCHANGE_RATE_API_URL = "https://open.er-api.com/v6/latest/{base_currency}"

REQUEST_TIMEOUT_SECONDS = 10


class CurrencyConverter:
    """OOP Class representing a Currency Converter instance."""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("EXCHANGERATE_API_KEY")

    def fetch_rates(self, base_currency):
        return fetch_exchange_rates(base_currency, self.api_key)

    def get_rate(self, base_currency, target_currency):
        return get_exchange_rate(base_currency, target_currency, self.api_key)

    def convert(self, amount, base_currency, target_currency):
        return convert_currency(amount, base_currency, target_currency, self.api_key)


def fetch_exchange_rates(base_currency, api_key=None):
    """
    Ask ExchangeRate-API for the latest rates relative to `base_currency`.
    Uses developer API key if set, or falls back to open keyless API automatically.
    """
    base_currency = validate_currency_code(base_currency)
    api_key = api_key or os.getenv("EXCHANGERATE_API_KEY")

    if api_key:
        url = EXCHANGE_RATE_API_URL.format(api_key=api_key, base_currency=base_currency)
    else:
        url = OPEN_EXCHANGE_RATE_API_URL.format(base_currency=base_currency)

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.exceptions.RequestException as error:
        raise APIError(f"Could not reach ExchangeRate API: {error}")

    if response.status_code != 200:
        raise APIError(f"ExchangeRate API returned error status {response.status_code}")

    data = response.json()

    if data.get("result") != "success":
        error_type = data.get("error-type", "unknown-error")
        raise APIError(f"ExchangeRate-API reported an error: {error_type}")

    rates = data.get("conversion_rates") or data.get("rates")
    if not rates:
        raise MissingDataError("The API response didn't include any exchange rates.")
    return rates


def get_exchange_rate(base_currency, target_currency, api_key=None):
    target_currency = validate_currency_code(target_currency)
    rates = fetch_exchange_rates(base_currency, api_key)
    if target_currency not in rates:
        raise MissingDataError(
            f"No exchange rate found for '{target_currency}'. Double-check the currency code."
        )
    return rates[target_currency]


def convert_currency(amount, base_currency, target_currency, api_key=None):
    """
    Convert an amount from base currency to target currency.
    Example: convert_currency(100, 'USD', 'NGN') -> 132917.0
    """
    amount = validate_amount(amount, field_name="amount to convert")
    rate = get_exchange_rate(base_currency, target_currency, api_key)
    converted_amount = round(amount * rate, 2)
    return converted_amount