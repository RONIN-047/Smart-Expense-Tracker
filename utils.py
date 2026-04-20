# utils.py - Validation, formatting helpers, and general constants
import datetime
import csv
from pathlib import Path
from typing import Tuple, Optional, Any, List

CATEGORIES: list[str] = ['Food', 'Travel', 'Shopping', 'Health', 'Education', 'Bills', 'Entertainment', 'Other']
CATEGORY_ICONS: dict[str, str] = {
    'food': '🍔',
    'travel': '🚗',
    'shopping': '🛍️',
    'health': '🏥',
    'education': '🎓',
    'bills': '💡',
    'entertainment': '🎮',
    'other': '📌'
}

def get_category_display(category: str) -> str:
    # Format category name with its corresponding emoji icon
    cat_lower = str(category).lower().strip()
    icon = CATEGORY_ICONS.get(cat_lower, '📌')
    # Prevent double-emoji if it's somehow already there
    if str(category).startswith(icon):
        return str(category)
    return f"{icon} {category}"

def validate_amount(value: Any) -> Tuple[bool, Optional[str]]:
    # Validate that the given string or number is a valid positive float.
    if not value or str(value).strip() == "":
        return False, "Amount cannot be empty."
    try:
        amount = float(value)
        if amount <= 0:
            return False, "Amount must be a positive number."
        return True, None
    except ValueError:
        return False, "Amount must be a valid number."

def validate_date(value: Any) -> Tuple[bool, Optional[str]]:
    # Validate that the given string strictly matches the YYYY-MM-DD format.
    if not value or str(value).strip() == "":
        return False, "Date cannot be empty."
    try:
        datetime.datetime.strptime(str(value), "%Y-%m-%d")
        return True, None
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format."

def format_currency(amount: float | str) -> str:
    # Format integer or float into a cleanly formatted Rupee string.
    try:
        val = float(amount)
        return f"Rs {val:,.2f}"
    except (ValueError, TypeError):
        return "Rs 0.00"

def format_month(yyyy_mm: str) -> str:
    """Convert a string like '2026-04' to 'April 2026'."""
    try:
        date_obj = datetime.datetime.strptime(yyyy_mm, "%Y-%m")
        return date_obj.strftime("%B %Y")
    except ValueError:
        return yyyy_mm

def get_today() -> str:
    """Return the current local date in YYYY-MM-DD format."""
    return datetime.datetime.today().strftime("%Y-%m-%d")

def export_to_csv(data: List[Tuple], filepath: str | Path) -> bool:
    """Iterate through data tuples and safely write to the target CSV path."""
    if not data:
        return False
    try:
        path = Path(filepath)
        with path.open(mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
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