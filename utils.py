# utils.py - Validation, formatting helpers, and general constants
import datetime
import csv

CATEGORIES = ['Food', 'Travel', 'Shopping', 'Health', 'Education', 'Bills', 'Entertainment', 'Other']
CATEGORY_ICONS = {
    'food': '🍔',
    'travel': '🚗',
    'shopping': '🛍️',
    'health': '🏥',
    'education': '🎓',
    'bills': '💡',
    'entertainment': '🎮',
    'other': '📌'
}

def get_category_display(category):
    cat_lower = str(category).lower().strip()
    icon = CATEGORY_ICONS.get(cat_lower, '📌')
    # Prevent double-emoji if it's somehow already there
    if str(category).startswith(icon):
        return category
    return f"{icon} {category}"


def validate_amount(value):
    # Return (True, None) if valid +ve number, else (False, error_message)
    if not value or str(value).strip() == "":
        return False, "Amount cannot be empty."
    try:
        amount = float(value)
        if amount <= 0:
            return False, "Amount must be a positive number."
        return True, None
    except ValueError:
        return False, "Amount must be a valid number."

def validate_date(value):
    # Return (True, None) if valid YYYY-MM-DD date, else (False, error_message)
    if not value or str(value).strip() == "":
        return False, "Date cannot be empty."
    try:
        datetime.datetime.strptime(value, "%Y-%m-%d")
        return True, None
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format."

def format_currency(amount):
    # Return amount formatted as string e.g. 'Rs 1,200.00'
    try:
        val = float(amount)
        return f"Rs {val:,.2f}"
    except (ValueError, TypeError):
        return "Rs 0.00"

def format_month(yyyy_mm):
    # Convert '2026-04' to 'April 2026'
    try:
        date_obj = datetime.datetime.strptime(yyyy_mm, "%Y-%m")
        return date_obj.strftime("%B %Y")
    except ValueError:
        return yyyy_mm          # Fallback to original string if format is wrong

def get_today():
    return datetime.datetime.today().strftime("%Y-%m-%d")

def export_to_csv(data, filepath):
    if not data:
        return False
    try:
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Standard headers based on expenses table format
            writer.writerow(["ID", "Amount", "Category", "Date", "Note"])
            writer.writerows(data)
        return True
    except IOError as e:
        print(f"Error exporting CSV: {e}")
        return False

# Quick test block to verify independently
if __name__ == "__main__":
    print("--- Testing utils.py ---")
    print(f"Categories loaded: {', '.join(CATEGORIES)}\n")
    print(f"validate_amount('150.5')  => {validate_amount('150.5')}")
    print(f"validate_amount('-10')    => {validate_amount('-10')}")
    print(f"validate_amount('abc')    => {validate_amount('abc')}\n")
    today = get_today()
    print(f"get_today()              => '{today}'")
    print(f"validate_date(today)     => {validate_date(today)}")
    print(f"validate_date('12-04-26')=> {validate_date('12-04-2026')}\n")
    print(f"format_currency(1234.5)  => '{format_currency(1234.5)}'")
    print(f"format_month('2026-04')  => '{format_month('2026-04')}'")