"""
Compares the estimated cost of traveling to two different destinations
by converting both into the SAME currency first for accurate comparison.
API keys are handled on the backend via environment variables (.env).
"""

from validators import validate_amount, validate_duration
from currency_converter import convert_currency


def compare_destinations(
    destination_a,
    cost_a,
    currency_a,
    duration_a,
    destination_b,
    cost_b,
    currency_b,
    duration_b,
    display_currency,
    api_key=None,
):
    cost_a = validate_amount(cost_a, field_name=f"{destination_a} cost")
    cost_b = validate_amount(cost_b, field_name=f"{destination_b} cost")
    duration_a = validate_duration(duration_a)
    duration_b = validate_duration(duration_b)

    # Convert both estimated costs into one common currency before comparing them.
    converted_a = convert_currency(cost_a, currency_a, display_currency, api_key)
    converted_b = convert_currency(cost_b, currency_b, display_currency, api_key)

    daily_a = round(converted_a / duration_a, 2)
    daily_b = round(converted_b / duration_b, 2)

    if converted_a < converted_b:
        cheaper = destination_a
    elif converted_b < converted_a:
        cheaper = destination_b
    else:
        cheaper = "Both of these destinations cost the same"

    return {
        "destination_a": {
            "name": destination_a,
            "total_cost": converted_a,
            "daily_cost": daily_a,
        },
        "destination_b": {
            "name": destination_b,
            "total_cost": converted_b,
            "daily_cost": daily_b,
        },
        "currency": display_currency,
        "cheaper_destination": cheaper,
    }
