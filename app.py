""" The Streamlit user interface for the Currency & Travel Budget Planner.
This file is the INTEGRATION point: it imports every other module and
wires them together into one working app.

Modules used here:
  - currency_converter.py  -> live currency conversion
  - trip_budget.py         -> budget math
  - expense.py              -> expense tracking
  - budget_report.py       -> save/load/export/report
  - country_comparison.py  -> compare two destinations
  - holiday_checker.py     -> public holiday warnings
  - travel_advisor.py      -> AI advice via Gemini
  - validators.py / exceptions.py -> used indirectly by everything above
Run it with:   streamlit run app.py"""

import json
import os
from datetime import date

import streamlit as st

from exceptions import BudgetPlannerError
from currency_converter import convert_currency
from trip_budget import TripBudget
from expense import ExpenseTracker
from budget_report import (
    save_budget_to_json,
    load_budget_from_json,
    export_expenses_to_csv,
    load_expenses_from_csv,
    generate_summary_report,
)
from country_comparison import compare_destinations
from holiday_checker import check_holiday_overlap
from travel_advisor import get_travel_advice


# Where we save data on disk so it can be reloaded later.
DATA_DIR = "data"
BUDGET_FILE = os.path.join(DATA_DIR, "budget.json")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.csv")

PAGES = [
    "Home",
    "Currency Converter",
    "Trip Budget",
    "Expense Tracker",
    "Country Comparison",
    "Holiday Checker",
    "AI Travel Advice",
    "Reports & Export",
]


def init_session_state():
    """
    Streamlit re-runs this ENTIRE script from top to bottom every time
    the user clicks a button or fills in a widget. `st.session_state`
    is a dictionary that SURVIVES those re-runs, so we use it to
    remember things — like the trip budget and expense list — between
    interactions. This function only sets things up the very first time.
    """
    if "trip_budget" not in st.session_state:
        st.session_state.trip_budget = None
    if "expense_tracker" not in st.session_state:
        st.session_state.expense_tracker = ExpenseTracker()


def show_error(error):
    """Display one of our custom exceptions as a friendly red error box."""
    st.error(str(error))

# SIDEBAR

def _load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
_load_env_file()


def render_sidebar():
    """Draws the sidebar navigation menu."""
    st.sidebar.title("✈️ Travel Budget Planner")
    page = st.sidebar.radio("Go to", PAGES)
    return page

# PAGES

def page_home():
    st.title("✈️ Currency & Travel Budget Planner")
    st.write(
        "Plan a trip budget, track what you actually spend, compare two "
        "destinations, check for public holidays, and get AI travel "
        "advice — all in one place."
    )
    st.write(
        "Start on the **Trip Budget** page to set up your trip, then use "
        "the other pages from the sidebar as you go."
    )

    if st.session_state.trip_budget:
        budget = st.session_state.trip_budget
        st.subheader("Your current trip")
        col1, col2, col3 = st.columns(3)
        col1.metric("Destination", budget.destination)
        col2.metric("Duration", f"{budget.duration_days} days")
        col3.metric("Total budget", f"{budget.total_budget()} {budget.currency}")


def page_currency_converter():
    st.title("💱 Currency Converter")

    col1, col2, col3 = st.columns(3)
    amount = col1.number_input("Amount", min_value=0.0, value=100.0, step=1.0)
    base_currency = col2.text_input("From currency", value="USD").upper()
    target_currency = col3.text_input("To currency", value="NGN").upper()

    if st.button("Convert", type="primary"):
        try:
            result = convert_currency(amount, base_currency, target_currency)
            st.success(f"{amount} {base_currency} = {result} {target_currency}")
        except BudgetPlannerError as error:
            show_error(error)


def page_trip_budget():
    st.title("💰 Trip Budget Calculator")

    col1, col2, col3 = st.columns(3)
    destination = col1.text_input("Destination", value="Lagos, Nigeria")
    duration_days = col2.number_input("Duration (days)", min_value=1, value=7, step=1)
    currency = col3.text_input("Currency", value="NGN").upper()

    st.write("Estimate your average cost **per day** for each category:")
    col1, col2 = st.columns(2)
    daily_accommodation = col1.number_input("Accommodation / day", min_value=0.0, value=50.0)
    daily_food = col2.number_input("Food / day", min_value=0.0, value=20.0)
    daily_transportation = col1.number_input("Transportation / day", min_value=0.0, value=10.0)
    daily_activities = col2.number_input("Activities / day", min_value=0.0, value=15.0)
    daily_miscellaneous = col1.number_input("Miscellaneous / day", min_value=0.0, value=10.0)

    if st.button("Calculate budget", type="primary"):
        try:
            budget = TripBudget(
                destination,
                duration_days,
                currency,
                daily_accommodation,
                daily_food,
                daily_transportation,
                daily_activities,
                daily_miscellaneous,
            )
            st.session_state.trip_budget = budget
            st.success("Budget calculated.see the breakdown below.")
        except BudgetPlannerError as error:
            show_error(error)

    if st.session_state.trip_budget:
        breakdown = st.session_state.trip_budget.breakdown()
        st.subheader("Budget breakdown")
        rows = [
            {"Category": key.replace("_", " ").title(), "Amount": value}
            for key, value in breakdown.items()
            if key not in ("destination", "duration_days", "currency")
        ]
        st.dataframe(rows, hide_index=True, use_container_width=True)

        col1, col2 = st.columns(2)
        col1.metric("Total budget", f"{breakdown['total_budget']} {breakdown['currency']}")
        col2.metric("Daily spending limit", f"{breakdown['daily_spending_limit']} {breakdown['currency']}")


def page_expense_tracker():
    st.title("🧾 Expense Tracker")
    tracker = st.session_state.expense_tracker
    budget = st.session_state.trip_budget
    default_currency = budget.currency if budget else "NGN"

    if budget:
        st.caption(f"Logging expenses for your trip to {budget.destination}. "
                   f"Record amounts in {budget.currency} to match your budget.")

    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        category = col1.selectbox(
            "Category", ["Accommodation", "Food", "Transportation", "Activities", "Miscellaneous"]
        )
        currency = col2.text_input("Currency", value=default_currency).upper()
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, value=0.0)
        expense_date = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Add expense")

        if submitted:
            try:
                tracker.add_expense(category, description, amount, currency, expense_date)
                st.success(f"Added {amount} {currency} under {category}.")
            except BudgetPlannerError as error:
                show_error(error)

    if tracker.expenses:
        st.subheader("Recorded expenses")
        st.dataframe(tracker.to_dict_list(), hide_index=True, use_container_width=True)

        st.subheader("Total by category")
        st.bar_chart(tracker.expenses_by_category())

        col1, col2 = st.columns(2)
        col1.metric("Total spent", f"{tracker.total_expenses()} {default_currency}")
        if budget:
            remaining = budget.remaining_budget(tracker.total_expenses())
            col2.metric("Remaining budget", f"{remaining} {budget.currency}")
    else:
        st.info("No expenses recorded yet — add one above.")

def page_country_comparison():
    st.title("🌍 Country Comparison")

    st.write("Compare the total estimated cost of two destinations, converted to the same currency.")
    display_currency = st.text_input("Compare costs in currency", value="USD").upper()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Destination A")
        dest_a = st.text_input("Name", value="Paris", key="dest_a_name")
        cost_a = st.number_input("Estimated total cost", min_value=0.0, value=1000.0, key="dest_a_cost")
        currency_a = st.text_input("Currency", value="EUR", key="dest_a_currency").upper()
        duration_a = st.number_input("Duration (days)", min_value=1, value=5, key="dest_a_duration")

    with col_b:
        st.subheader("Destination B")
        dest_b = st.text_input("Name", value="Nairobi", key="dest_b_name")
        cost_b = st.number_input("Estimated total cost", min_value=0.0, value=800.0, key="dest_b_cost")
        currency_b = st.text_input("Currency", value="USD", key="dest_b_currency").upper()
        duration_b = st.number_input("Duration (days)", min_value=1, value=5, key="dest_b_duration")

    if st.button("Compare", type="primary"):
        try:
            result = compare_destinations(
                dest_a, cost_a, currency_a, duration_a,
                dest_b, cost_b, currency_b, duration_b,
                display_currency,
            )
            st.dataframe(
                [result["destination_a"], result["destination_b"]],
                hide_index=True,
                use_container_width=True,
            )
            st.success(f"Cheaper destination: {result['cheaper_destination']}")
        except BudgetPlannerError as error:
            show_error(error)


def page_holiday_checker():
    st.title("📅 Public Holiday Checker")

    country_code = st.text_input("Destination country code (e.g. NG, US, GB)", value="NG").upper()
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Trip start date")
    end_date = col2.date_input("Trip end date")

    if st.button("Check for holidays", type="primary"):
        try:
            holidays = check_holiday_overlap(
                country_code, start_date.isoformat(), end_date.isoformat()
            )
            if holidays:
                st.warning(f"Your trip overlaps with {len(holidays)} public holiday(s):")
                st.dataframe(
                    [{"Date": h["date"], "Holiday": h["name"]} for h in holidays],
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.success("No public holidays fall within your travel dates.")
        except BudgetPlannerError as error:
            show_error(error)

def page_ai_advice():
    st.title("🤖 AI Travel Advice")
    budget = st.session_state.trip_budget

    if not budget:
        st.info("Calculate a trip budget first (see the Trip Budget page) to get personalized advice.")
        return

    st.write(
        f"Get AI-generated budgeting advice for your {budget.duration_days}-day "
        f"trip to {budget.destination}."
    )

    if st.button("Get advice", type="primary"):
        with st.spinner("Asking AI for advice..."):
            try:
                advice = get_travel_advice(
                    budget.destination,
                    budget.duration_days,
                    budget.total_budget(),
                    budget.currency,
                    budget.daily_spending_limit(),
                )
                st.write(advice)
            except BudgetPlannerError as error:
                show_error(error)


def page_reports():
    st.title("📊 Reports & Export")
    budget = st.session_state.trip_budget
    tracker = st.session_state.expense_tracker

    if not budget:
        st.info("Calculate a trip budget first (see the Trip Budget page) to generate a report.")
        return

    report_text = generate_summary_report(budget.breakdown(), tracker.total_expenses())
    st.text(report_text)

    os.makedirs(DATA_DIR, exist_ok=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Budget")
        if st.button("Save budget to disk"):
            try:
                save_budget_to_json(budget.breakdown(), BUDGET_FILE)
                st.success(f"Saved to {BUDGET_FILE}")
            except BudgetPlannerError as error:
                show_error(error)
        st.download_button(
            "Download budget as JSON",
            data=json.dumps(budget.breakdown(), indent=2),
            file_name="budget.json",
            mime="application/json",
        )

    with col2:
        st.subheader("Expenses")
        if tracker.expenses:
            if st.button("Save expenses to disk"):
                try:
                    export_expenses_to_csv(tracker.to_dict_list(), EXPENSES_FILE)
                    st.success(f"Saved to {EXPENSES_FILE}")
                except BudgetPlannerError as error:
                    show_error(error)

            # Build the CSV text in memory (without touching disk) so
            # the download button always has something to offer, even
            # if the user never clicks "Save expenses to disk".
            import csv
            import io

            buffer = io.StringIO()
            fieldnames = list(tracker.to_dict_list()[0].keys())
            writer = csv.DictWriter(buffer, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tracker.to_dict_list())

            st.download_button(
                "Download expenses as CSV",
                data=buffer.getvalue(),
                file_name="expenses.csv",
                mime="text/csv",
            )
        else:
            st.caption("No expenses recorded yet.")

    st.divider()
    if st.button("Load previously saved data from disk"):
        try:
            budget_data = load_budget_from_json(BUDGET_FILE)
            st.json(budget_data)
        except BudgetPlannerError as error:
            show_error(error)

        if os.path.exists(EXPENSES_FILE):
            try:
                rows = load_expenses_from_csv(EXPENSES_FILE)
                st.dataframe(rows, hide_index=True, use_container_width=True)
            except BudgetPlannerError as error:
                show_error(error)

# MAIN

def main():
    st.set_page_config(page_title="Travel Budget Planner", page_icon="✈️", layout="wide")
    init_session_state()
    page = render_sidebar()

    # This dictionary maps each sidebar label to the function that draws that page, so we can call the right one with a single lookup instead of a long chain of if statements.
    page_functions = {
        "Home": page_home,
        "Currency Converter": page_currency_converter,
        "Trip Budget": page_trip_budget,
        "Expense Tracker": page_expense_tracker,
        "Country Comparison": page_country_comparison,
        "Holiday Checker": page_holiday_checker,
        "AI Travel Advice": page_ai_advice,
        "Reports & Export": page_reports,
    }
    page_functions[page]()


if __name__ == "__main__":
    main()
