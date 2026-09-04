# Complete Code Explanation for `app.py`

This document provides a **bit-by-bit, line-by-line explanation** of `app.py`, explaining what every line does, why every function exists, and how all parts connect together to form the **Travel Budget Planner** web application.

---

## 1. High-Level Architecture & Overview

In Streamlit applications, `app.py` serves as the **Integration Point (Control Room)**. 
- It imports logic from every other backend file (`currency_converter.py`, `trip_budget.py`, `expense.py`, `budget_report.py`, `country_comparison.py`, `holiday_checker.py`, `travel_advisor.py`, `validators.py`, and `exceptions.py`).
- It connects those backend functions to interactive visual components (buttons, text boxes, tables, metrics, and charts).

### 💡 Key Concept: How Streamlit Works
Unlike standard web apps (Django/Flask) or desktop apps (Tkinter), **Streamlit re-runs `app.py` from top to bottom every single time a user interacts with a widget** (clicking a button, entering text, changing a dropdown). 

Because of this re-running behavior:
- Variables inside normal functions disappear when a page reloads.
- To remember data between clicks (like your active trip budget or logged expenses), Streamlit provides a persistent dictionary called `st.session_state`.

---

## 2. Imports and Global Configuration (Lines 1 – 53)

```python
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
```

### Why these imports exist:
- **`json` & `os`**: Used for creating local storage folders (`data/`) and saving/loading budget files.
- **`date`**: Used to supply today's date as a default value when logging new expenses.
- **`streamlit as st`**: The main Web Framework powering all buttons, inputs, titles, columns, and navigation.
- **Custom Project Modules**:
  - `BudgetPlannerError`: The base custom exception class used to catch application errors cleanly.
  - `convert_currency`: Converts money values between currencies using live or fallback exchange rates.
  - `TripBudget`: The OOP class that calculates total budget math and daily spending limits.
  - `ExpenseTracker`: The OOP container class that stores and manages recorded expenses.
  - `save_budget_to_json`, `load_budget_from_json`, `export_expenses_to_csv`, `load_expenses_from_csv`, `generate_summary_report`: Functions for saving, loading, exporting, and building text reports.
  - `compare_destinations`: Compares costs of two travel destinations in a standardized currency.
  - `check_holiday_overlap`: Connects to Nager.Date API to check if trip dates overlap public holidays.
  - `get_travel_advice`: Connects to Google Gemini AI for customized travel tips.

---

### Global File Paths & Constants (Lines 38 – 52)

```python
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
```

### Why these exist:
- **`DATA_DIR` / `BUDGET_FILE` / `EXPENSES_FILE`**: Centralizes file paths where saved data (`data/budget.json` and `data/expenses.csv`) is stored on disk so every page uses identical file locations.
- **`PAGES`**: A list of strings defining all 8 menu options shown in the left sidebar.

---

## 3. Core Helper Functions (Lines 55 – 96)

### Function 1: `init_session_state()`
```python
def init_session_state():
    if "trip_budget" not in st.session_state:
        st.session_state.trip_budget = None
    if "expense_tracker" not in st.session_state:
        st.session_state.expense_tracker = ExpenseTracker()
```
- **Why it exists**: Initializes long-term memory (`st.session_state`) on the user's first visit.
- **What it does**:
  - `st.session_state.trip_budget`: Stores the active `TripBudget` object (starts as `None` until calculated).
  - `st.session_state.expense_tracker`: Stores an instance of `ExpenseTracker` so added expenses aren't lost when switching pages.

---

### Function 2: `show_error(error)`
```python
def show_error(error):
    st.error(str(error))
```
- **Why it exists**: Provides a clean, standardized error box when exceptions occur.
- **What it does**: Takes any caught `BudgetPlannerError` exception and displays a styled red error message box in the Streamlit UI instead of crashing the app with a raw Python stack trace.

---

### Function 3: `_load_env_file()`
```python
def _load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
```
- **Why it exists**: Security & Backend Configuration.
- **What it does**: Checks for a `.env` file in the project folder and automatically loads developer environment variables (`EXCHANGERATE_API_KEY`, `GEMINI_API_KEY`) into Python's `os.environ`. This allows the backend to handle keys automatically without forcing end-users to type keys into the web UI.

---

### Function 4: `render_sidebar()`
```python
def render_sidebar():
    st.sidebar.title("✈️ Travel Budget Planner")
    page = st.sidebar.radio("Go to", PAGES)
    return page
```
- **Why it exists**: Handles main navigation.
- **What it does**: Renders the title and radio button selection list in the left sidebar, returning the string name of the selected page (e.g. `"Trip Budget"`).

---

## 4. Page View Functions (Lines 101 – 396)

### Page 1: `page_home()`
```python
def page_home():
    st.title("✈️ Currency & Travel Budget Planner")
    st.write("Plan a trip budget, track what you actually spend...")
    
    if st.session_state.trip_budget:
        budget = st.session_state.trip_budget
        st.subheader("Your current trip")
        col1, col2, col3 = st.columns(3)
        col1.metric("Destination", budget.destination)
        col2.metric("Duration", f"{budget.duration_days} days")
        col3.metric("Total budget", f"{budget.total_budget()} {budget.currency}")
```
- **Why it exists**: Serves as the landing dashboard.
- **What it does**: Displays welcome text and a quick start guide. If a trip budget has already been calculated, it uses `st.columns(3)` and `st.metric()` to display a clean summary card (Destination, Duration, and Total Budget).

---

### Page 2: `page_currency_converter()`
```python
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
```
- **Why it exists**: Performs standalone currency conversions.
- **What it does**: Creates three side-by-side inputs (Amount, From Currency, To Currency). When the user clicks **Convert**, it calls `convert_currency()` from `currency_converter.py` and presents the result in a green success banner (`st.success`). If validation or API errors occur, it catches `BudgetPlannerError` and calls `show_error()`.

---

### Page 3: `page_trip_budget()`
```python
def page_trip_budget():
    st.title("💰 Trip Budget Calculator")
    ...
```
- **Why it exists**: Calculates and plans total travel budgets.
- **What it does**:
  1. Captures destination, trip length, currency, and daily cost estimates for Accommodation, Food, Transport, Activities, and Miscellaneous.
  2. Upon clicking **Calculate budget**, creates a new `TripBudget` object and saves it into `st.session_state.trip_budget`.
  3. Displays an itemized budget table (`st.dataframe`) and key metrics for **Total Budget** and **Daily Spending Limit**.

---

### Page 4: `page_expense_tracker()`
```python
def page_expense_tracker():
    st.title("🧾 Expense Tracker")
    tracker = st.session_state.expense_tracker
    ...
```
- **Why it exists**: Logs and analyzes actual spending during a trip.
- **What it does**:
  1. Uses `st.form("add_expense_form")` to let users input expense categories, descriptions, amounts, and dates.
  2. Adds submitted expenses to `st.session_state.expense_tracker`.
  3. Renders a recorded expense history table (`st.dataframe`) and a category spending breakdown bar chart (`st.bar_chart`).
  4. Automatically subtracts total spent from `st.session_state.trip_budget` to display **Remaining Budget** in real-time.

---

### Page 5: `page_country_comparison()`
```python
def page_country_comparison():
    st.title("🌍 Country Comparison")
    ...
```
- **Why it exists**: Compares estimated travel costs between two destinations.
- **What it does**: Takes input for Destination A and Destination B (costs, durations, and currencies), standardizes both costs into a single display currency using `compare_destinations()`, and highlights the cheaper destination.

---

### Page 6: `page_holiday_checker()`
```python
def page_holiday_checker():
    st.title("📅 Public Holiday Checker")
    ...
```
- **Why it exists**: Warns travelers if trip dates conflict with public holidays.
- **What it does**: Takes a country code (e.g. `NG`, `US`, `GB`) and trip start/end dates, calls `check_holiday_overlap()`, and displays a yellow warning box (`st.warning`) with a holiday schedule if any overlaps are found.

---

### Page 7: `page_ai_advice()`
```python
def page_ai_advice():
    st.title("🤖 AI Travel Advice")
    ...
```
- **Why it exists**: Delivers intelligent, AI-powered travel advice.
- **What it does**: Checks if a trip budget exists. If present, calls `get_travel_advice()` while displaying a loading spinner (`with st.spinner(...)`). Uses Google Gemini AI (or built-in fallback tips if no key is set) to display personalized cost-cutting recommendations.

---

### Page 8: `page_reports()`
```python
def page_reports():
    st.title("📊 Reports & Export")
    ...
```
- **Why it exists**: Provides data persistence, summary reporting, and local file exports.
- **What it does**:
  1. Displays a formatted text summary report using `generate_summary_report()`.
  2. Provides **Save to disk** buttons that write `data/budget.json` and `data/expenses.csv`.
  3. Provides interactive **Download** buttons (`st.download_button`) allowing users to download JSON and CSV files directly through their browser.
  4. Provides a **Load saved data** button to read previously saved files from disk back into the app.

---

## 5. Main Execution Flow (Lines 402 – 424)

```python
def main():
    st.set_page_config(page_title="Travel Budget Planner", page_icon="✈️", layout="wide")
    init_session_state()
    page = render_sidebar()

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
```

### Why `main()` exists and how execution works:
1. `st.set_page_config(...)`: Sets the browser tab title ("Travel Budget Planner"), favicon ("✈️"), and layout mode (`"wide"`).
2. `init_session_state()`: Ensures long-term session memory is ready.
3. `page = render_sidebar()`: Draws the navigation menu and captures which page the user clicked.
4. **Dictionary Dispatch (`page_functions`)**: Maps each page name string directly to its corresponding Python function (e.g. `"Expense Tracker": page_expense_tracker`).
5. `page_functions[page]()`: Executes the selected page function cleanly without needing long `if / elif / else` chains.
6. `if __name__ == "__main__": main()`: Ensures `main()` runs automatically whenever the file is launched via `streamlit run app.py`.

---

## 📌 Summary Checklist of Functions

| Function Name | Location | Primary Purpose |
| :--- | :--- | :--- |
| `init_session_state()` | Line 55 | Initializes persistent session dictionary memory for `trip_budget` and `expense_tracker`. |
| `show_error(error)` | Line 69 | Displays application exceptions cleanly in red error boxes. |
| `_load_env_file()` | Line 78 | Automatically loads developer keys from `.env` file into system environment. |
| `render_sidebar()` | Line 91 | Draws the left navigation sidebar and returns selected page name. |
| `page_home()` | Line 101 | Renders home dashboard and summary metrics for active trip. |
| `page_currency_converter()` | Line 122 | Renders Currency Converter UI and calls `convert_currency()`. |
| `page_trip_budget()` | Line 138 | Renders budget calculator form, creates `TripBudget` object, and displays breakdown. |
| `page_expense_tracker()` | Line 186 | Renders expense logging form, updates `ExpenseTracker`, and displays spending charts. |
| `page_country_comparison()` | Line 229 | Renders destination comparison UI and calls `compare_destinations()`. |
| `page_holiday_checker()` | Line 267 | Renders holiday checker form and calls `check_holiday_overlap()`. |
| `page_ai_advice()` | Line 292 | Renders AI advice UI and calls `get_travel_advice()`. |
| `page_reports()` | Line 320 | Renders text summary report and handles JSON/CSV file saving & downloads. |
| `main()` | Line 402 | Configures page settings, initializes state, renders sidebar, and routes execution to selected page. |
