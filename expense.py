# expense.py - Core logic for adding, fetching, and deleting expenses
import sqlite3
import db
import utils
from typing import List

def add_expense(amount: float | str, category: str, date: str, note: str = '', trans_type: str = 'Expense') -> bool:
    """Insert a new transaction into the database. Returns True on success."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO expenses (amount, category, date, note, type)
                VALUES (?, ?, ?, ?, ?)
            ''', (float(amount), category, date, note, trans_type))
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Error adding transaction: {e}")
        return False

def get_all_expenses() -> List[sqlite3.Row]:
    """Return all expense rows, ordered by date DESC."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM expenses ORDER BY date DESC, id DESC')
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching expenses: {e}")
        return []

def get_expense_by_id(expense_id: int) -> sqlite3.Row:
    """Return a single expense row by its ID."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Error fetching expense by id: {e}")
        return None

def get_expenses_by_category(category: str) -> List[sqlite3.Row]:
    """Return all expenses for a specific category."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM expenses 
                WHERE category = ? 
                ORDER BY date DESC, id DESC
            ''', (category,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching expenses by category: {e}")
        return []

def delete_expense(expense_id: int) -> bool:
    """Delete the expense with the given ID. Returns True on success."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Error deleting expense: {e}")
        return False

def update_expense(expense_id: int, amount: float | str, category: str, date: str, note: str, trans_type: str) -> bool:
    """Update an existing transaction in the database. Returns True on success."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE expenses 
                SET amount = ?, category = ?, date = ?, note = ?, type = ?
                WHERE id = ?
            ''', (float(amount), category, date, note, trans_type, expense_id))
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Error updating transaction: {e}")
        return False

def get_all_categories() -> List[str]:
    """Return a unique list of all categories used, combining database records with utils defaults."""
    categories = list(utils.CATEGORIES)
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT category FROM expenses')
            for row in cursor.fetchall():
                if row['category'] not in categories:
                    categories.append(row['category'])
            return categories
    except sqlite3.Error as e:
        print(f"Error fetching categories: {e}")
        return categories
