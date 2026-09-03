"""
Handles saving and loading data to/from disk:
  - save/load a trip's budget as JSON
  - export a trip's expenses to CSV, and read them back
  - build a plain-text budget summary report
"""

import json
import csv
import os

from exceptions import FileHandlingError


class BudgetReport:
    """OOP Wrapper for building, saving, and loading travel budget reports."""

    def __init__(self, budget_breakdown=None, total_spent=0.0):
        self.budget_breakdown = budget_breakdown or {}
        self.total_spent = total_spent

    def generate_summary(self):
        return generate_summary_report(self.budget_breakdown, self.total_spent)

    def save_json(self, filepath):
        return save_budget_to_json(self.budget_breakdown, filepath)

    @staticmethod
    def load_json(filepath):
        return load_budget_from_json(filepath)

    @staticmethod
    def export_csv(expense_dicts, filepath):
        return export_expenses_to_csv(expense_dicts, filepath)

    @staticmethod
    def load_csv(filepath):
        return load_expenses_from_csv(filepath)


def save_budget_to_json(budget_data, filepath):
    """
    Save a dictionary of budget data (e.g. from TripBudget.breakdown())
    to a JSON file.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(budget_data, file, indent=2)
    except OSError as error:
        raise FileHandlingError(f"Could not write budget to '{filepath}': {error}")


def load_budget_from_json(filepath):
    if not os.path.exists(filepath):
        raise FileHandlingError(f"No saved budget file found at '{filepath}'.")

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        raise FileHandlingError(f"'{filepath}' is not a valid JSON file: {error}")
    except OSError as error:
        raise FileHandlingError(f"Could not read '{filepath}': {error}")


def export_expenses_to_csv(expense_dicts, filepath):
    if not expense_dicts:
        raise FileHandlingError("There are no expenses to export.")
    fieldnames = list(expense_dicts[0].keys())
    try:
        with open(filepath, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(expense_dicts)
    except OSError as error:
        raise FileHandlingError(f"Could not write expenses to '{filepath}': {error}")


def load_expenses_from_csv(filepath):
    if not os.path.exists(filepath):
        raise FileHandlingError(f"No expense file found at '{filepath}'.")
    try:
        with open(filepath, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return list(reader)
    except (OSError, csv.Error) as error:
        raise FileHandlingError(f"Could not read '{filepath}': {error}")


def generate_summary_report(budget_breakdown, total_spent=0.0):
    if not budget_breakdown:
        return "No budget data available."

    lines = [
        "========================================",
        "          TRAVEL BUDGET REPORT          ",
        "========================================",
        f"Destination:  {budget_breakdown.get('destination', 'N/A')}",
        f"Duration:     {budget_breakdown.get('duration_days', 'N/A')} days",
        f"Currency:     {budget_breakdown.get('currency', 'N/A')}",
        "----------------------------------------",
        "ESTIMATED COSTS:",
        f"  Accommodation:  {budget_breakdown.get('accommodation', 0.0)}",
        f"  Food:           {budget_breakdown.get('food', 0.0)}",
        f"  Transportation: {budget_breakdown.get('transportation', 0.0)}",
        f"  Activities:     {budget_breakdown.get('activities', 0.0)}",
        f"  Miscellaneous:  {budget_breakdown.get('miscellaneous', 0.0)}",
        "----------------------------------------",
        f"TOTAL BUDGET:         {budget_breakdown.get('total_budget', 0.0)}",
        f"DAILY SPENDING LIMIT: {budget_breakdown.get('daily_spending_limit', 0.0)}",
        f"TOTAL SPENT SO FAR:   {total_spent}",
        "========================================",
    ]
    return "\n".join(lines)