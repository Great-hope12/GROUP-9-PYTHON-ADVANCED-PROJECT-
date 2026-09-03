"""
exceptions.py
--------------
This file defines all the CUSTOM ERROR TYPES ("exceptions") used across
the Currency & Travel Budget Planner project.
"""
class BudgetPlannerError(Exception):
    """Base class for every custom error in this project."""
    pass
class InvalidCurrencyError(BudgetPlannerError):
    """Raised when a currency code isn't a valid 3-letter code for example the user typed 'DOLLARS' instead of 'USD')."""
    pass
class InvalidAmountError(BudgetPlannerError):
    """Raised when a money amount is missing, not a number or negative."""
    pass
class InvalidDurationError(BudgetPlannerError):
    """Raised when the number of days is invalid for example zero or negative or not a whole number."""
    pass
class InvalidDateError(BudgetPlannerError):
    """Raised when a date string can't be parsed, or a start date falls after an end date."""
    pass
class InvalidCountryCodeError(BudgetPlannerError):
    """Raised when a country code isn't a valid 2-letter code for example 'NIGERIA' instead of 'NG')."""
    pass
class APIError(BudgetPlannerError):
    """Raised when an external API (ExchangeRate-API, Nager.Date,
    Gemini) reports an error or can't be reached at all — no internet
    connection, invalid API key, timeout, etc."""
    pass
class MissingDataError(BudgetPlannerError):
    """Raised when data we expected to find is not there."""
    pass
class FileHandlingError(BudgetPlannerError):
    """Raised when reading or writing a file on disk fails, or the file turns out to be missing/corrupted."""
    pass