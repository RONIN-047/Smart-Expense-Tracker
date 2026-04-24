# Expense Tracker

**Name:** Abiel Sudeept Kumar  
**Enrollment Number:** 2023-310-019

---

A personal expense tracking app I built as a project. It runs entirely on your desktop — no internet, no accounts, no cloud. Just open it and start logging your spending.

Built with Python and CustomTkinter. All data is stored locally in a SQLite database on your machine.

---

## What it does

- Add expenses with a category, date, and optional note
- Browse all your expenses grouped by date
- Set monthly budgets (total and per category) and see when you're close to or over the limit
- View spending breakdowns with charts — pie chart by category, bar chart, and a monthly trend line
- Export everything to a CSV file you can open in Excel or Google Sheets

---

## Getting started

You need Python 3.10 or higher. Then install the dependencies:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install customtkinter matplotlib tkcalendar
```

Then just run it:

```bash
python main.py
```

---

## Project structure

```
main.py              # App entry point, window and sidebar
db.py                # Database connection and schema
expense.py           # Add, fetch, delete expenses
analytics.py         # Charts and budget calculations
utils.py             # Formatting, validation, helpers
views/
  dashboard.py       # Home screen with summary cards and charts
  add_expense.py     # Form to log a new expense
  browse.py          # Full expense list grouped by date
  budget.py          # Set and monitor budgets
  monthly.py         # Monthly history with trend chart
  export_csv.py      # Export data to CSV
  shared.py          # Shared colors and helper functions
```

---

## Tech used

- **Python 3.10+**
- **CustomTkinter** — for the UI
- **Matplotlib** — for charts
- **tkcalendar** — for the date picker
- **SQLite** — for local data storage (built into Python, no setup needed)

---

## Notes

- The database file (`expenses.db`) is created automatically on first run in the same folder as the app
- Nothing is sent anywhere — all data stays on your computer
- If you delete `expenses.db`, all your data is gone, so back it up if you care about it
