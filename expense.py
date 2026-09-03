"""
expense.py
-----------
Defines the Expense data model (one recorded expense) and an
ExpenseTracker (a collection of expenses for a trip, with helper
methods to total and organize them).

NOTE ON CURRENCY: to keep this beginner project simple, the tracker
assumes every expense is recorded in the SAME currency as your trip
budget. If you paid for something in a different currency, convert the
amount first using the Currency Converter page before logging it here.
"""

from datetime import date

from exceptions import MissingDataError
from validators import validate_amount


class Expense:
    """
    A single travel expense.

    Attributes:
        category (str): e.g. 'Food', 'Transport', 'Accommodation'
        description (str): a short note about the expense
        amount (float): how much was spent
        currency (str): the currency it was spent in, e.g. 'NGN'
        expense_date (date): the date the expense happened
    """

    def __init__(self, category, description, amount, currency, expense_date=None):
        if not category:
            raise MissingDataError("An expense needs a category.")

        # Calling validate_amount() here means an Expense object can
        # NEVER be created with a missing/negative/non-numeric amount —
        # the error happens immediately, right where the bad data came in.
        self.amount = validate_amount(amount, field_name="expense amount")

        self.category = category.strip().title()
        self.description = (description or "").strip()
        self.currency = (currency or "").strip().upper()
        # If the caller didn't supply a date, default to today.
        self.expense_date = expense_date or date.today()

    def to_dict(self):
        """Turn this Expense into a plain dictionary — used by
        budget_report.py when saving to JSON/CSV."""
        return {
            "category": self.category,
            "description": self.description,
            "amount": self.amount,
            "currency": self.currency,
            "date": self.expense_date.isoformat()
            if hasattr(self.expense_date, "isoformat")
            else str(self.expense_date),
        }

    def __repr__(self):
        return f"Expense({self.category}, {self.amount} {self.currency})"


class ExpenseTracker:
    """
    Holds a list of Expense objects for one trip and provides helper
    methods to analyze them.
    """

    def __init__(self):
        self.expenses = []

    def add_expense(self, category, description, amount, currency, expense_date=None):
        """Create an Expense and store it. Returns the new Expense."""
        expense = Expense(category, description, amount, currency, expense_date)
        self.expenses.append(expense)
        return expense

    def total_expenses(self):
        """Add up the amount of every recorded expense."""
        return round(sum(expense.amount for expense in self.expenses), 2)

    def expenses_by_category(self):
        """
        Group expenses by category and total each group.
        Returns a dict like {'Food': 120.0, 'Transport': 45.5}.
        """
        totals = {}
        for expense in self.expenses:
            totals[expense.category] = totals.get(expense.category, 0) + expense.amount
        return {category: round(total, 2) for category, total in totals.items()}

    def remaining_budget(self, total_budget):
        """ How much of total budget is left after subtracting every recorded expense """
        total_budget = validate_amount(total_budget, field_name="total budget")
        return round(total_budget - self.total_expenses(), 2)

    def to_dict_list(self):
        """This converts every Expense into a dictionary"""
        return [expense.to_dict() for expense in self.expenses]
