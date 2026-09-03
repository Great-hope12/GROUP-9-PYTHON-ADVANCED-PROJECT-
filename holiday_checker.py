""" This Checks whether a trip's travel dates overlap with public holidays in
the destination country, using the free Nager.Date public holiday API
(https://date.nager.at/). No API key is required for this one.
"""

import requests

from exceptions import InvalidCountryCodeError, APIError
from validators import validate_country_code, validate_date_range

NAGER_API_URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
REQUEST_TIMEOUT_SECONDS = 10


def get_public_holidays(country_code, year):
    """
    Fetch every public holiday for `country_code` in a given `year`.
    Returns a list of dicts, each with (at least) 'date' and 'name' keys.
    """
    country_code = validate_country_code(country_code)
    url = NAGER_API_URL.format(year=year, country_code=country_code)

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.exceptions.RequestException as error:
        raise APIError(f"Could not reach the Nager.Date API: {error}")

    # Nager.Date replies with 204 No Content when it doesn't recognize
    # the country/year combination — that's our signal for "bad country code".
    if response.status_code == 204:
        raise InvalidCountryCodeError(
            f"No holiday data found for country code '{country_code}'. "
            "Double check it's a valid 2-letter code, e.g. 'NG', 'US', 'GB'."
        )
    if response.status_code != 200:
        raise APIError(f"Nager.Date API returned an error (status {response.status_code}).")

    return response.json()


def check_holiday_overlap(country_code, start_date_str, end_date_str):
    """
    Find which public holidays (if any) fall between the trip's start
    and end dates, inclusive.

    Returns a list of overlapping holiday dicts — an empty list means
    no holidays fall during the trip.
    """
    start_date, end_date = validate_date_range(start_date_str, end_date_str)

    # A trip can span two calendar years (e.g. Dec 28 -> Jan 3), so we
    # check every year the trip touches, not just the start year.
    years_to_check = range(start_date.year, end_date.year + 1)

    overlapping_holidays = []
    for year in years_to_check:
        holidays = get_public_holidays(country_code, year)
        for holiday in holidays:
            holiday_date = holiday.get("date")
            # Holiday dates come back as 'YYYY-MM-DD' strings, which sort
            # the same alphabetically as chronologically — so we can
            # compare them directly against our start/end dates.
            if holiday_date and start_date.isoformat() <= holiday_date <= end_date.isoformat():
                overlapping_holidays.append(holiday)

    return overlapping_holidays
