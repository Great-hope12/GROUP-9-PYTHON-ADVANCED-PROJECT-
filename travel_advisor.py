"""
Talks to Google's Gemini API to generate personalized travel budget advice:
ways to cut costs, whether the daily spending limit looks realistic, and general budgeting tips.

The developer configures GEMINI_API_KEY in environment variables or a .env file.
If no key is configured, practical built-in advice is provided automatically.
"""

import os
import requests
from exceptions import APIError, MissingDataError

GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
REQUEST_TIMEOUT_SECONDS = 30


def _build_prompt(destination, duration_days, total_budget, currency, daily_spending_limit):
    return (
        f"I'm planning a {duration_days} day trip to {destination}. "
        f"My total budget is {total_budget} {currency}, which works out "
        f"to about {daily_spending_limit} {currency} per day. "
        "Please give me: "
        "1) 3 practical ways to cut costs on this trip, "
        "2) whether my daily spending limit seems realistic for this destination, "
        "and 3) one general budgeting tip. "
        "Keep the whole answer under 150 words and use simple language."
    )


def get_travel_advice(
    destination, duration_days, total_budget, currency, daily_spending_limit, api_key=None
):
    api_key = api_key or os.getenv("GEMINI_API_KEY")

    if not api_key:
        return (
            f"💡 **Smart Travel Budgeting Guide for {destination}**:\n\n"
            f"• **Daily Allowance Target**: Your budget of {daily_spending_limit} {currency}/day over {duration_days} days is your primary benchmark.\n"
            f"• **Accommodation Strategy**: Book early or explore verified local guesthouses outside peak tourist centers.\n"
            f"• **Transport Savings**: Use local transit passes or verified rideshare services instead of airport taxis.\n"
            f"• **Food & Dining**: Save up to 50% on dining by exploring authentic local food halls and markets.\n\n"
            f"*(Note for Developer: Add `GEMINI_API_KEY` to your environment or `.env` file to enable live AI responses.)*"
        )

    prompt = _build_prompt(destination, duration_days, total_budget, currency, daily_spending_limit)

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    try:
        response = requests.post(
            GEMINI_API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT_SECONDS
        )
    except requests.exceptions.RequestException as error:
        raise APIError(f"Could not reach Gemini API: {error}")

    if response.status_code != 200:
        raise APIError(
            f"Gemini API returned an error (status {response.status_code}): {response.text[:200]}"
        )

    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise MissingDataError("Gemini response did not contain any advice text.")
