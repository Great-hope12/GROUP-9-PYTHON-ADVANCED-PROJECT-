# ✈️ Currency & Travel Budget Planner

A Streamlit app for planning a trip budget, tracking expenses, comparing
destinations, checking for public holidays, and getting AI travel advice.

## Setup

1. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the app:
   ```
   streamlit run app.py
   ```
3. Open the app in your browser (Streamlit will print the local URL,
   usually `http://localhost:8501`).

## API keys

Two features need a free API key, entered directly in the app's sidebar
(nothing to configure in code):

| Feature | API | Get a key |
|---|---|---|
| Currency Converter, Country Comparison | ExchangeRate-API | https://www.exchangerate-api.com/ |
| AI Travel Advice | Gemini API | https://aistudio.google.com/apikey |

The Public Holiday Checker uses the free [Nager.Date](https://date.nager.at/)
API, which needs no key at all.

## Project structure

| File | Responsibility |
|---|---|
| `exceptions.py` | Custom error types used across every module |
| `validators.py` | Input validation (currencies, amounts, dates, etc.) |
| `currency_converter.py` | Live currency conversion (ExchangeRate-API) |
| `trip_budget.py` | Trip budget math (accommodation, food, etc.) |
| `expense.py` | Expense data model + tracker |
| `budget_report.py` | Save/load JSON & CSV, generate a summary report |
| `country_comparison.py` | Compare the cost of two destinations |
| `holiday_checker.py` | Public holiday warnings (Nager.Date API) |
| `travel_advisor.py` | AI budgeting advice (Gemini API) |
| `app.py` | Streamlit UI — ties every module together |

## Notes / possible extensions

- The Expense Tracker assumes every expense is logged in the same
  currency as your trip budget. A natural next step would be to convert
  each expense automatically using `currency_converter.py`.
- Saved data (`data/budget.json`, `data/expenses.csv`) lives in a local
  `data/` folder created the first time you save from the Reports page.
