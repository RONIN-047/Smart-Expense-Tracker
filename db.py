# db.py - Database connection, schema creation, and budget handling
import sqlite3
import sys
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

def get_db_path() -> Path:
    """Return the absolute path to the expenses.db file, safe for PyInstaller .exe."""
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).resolve().parent
    return base / 'expenses.db'

@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Create and reliably yield a connection to expenses.db."""
    conn = None
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row 
        yield conn
    finally:
        if conn:
            conn.close()

def initialise_db() -> bool:
    """Create expenses and budgets tables if they do not exist, and handle schema updates."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    note TEXT DEFAULT '',
                    type TEXT DEFAULT 'Expense'
                )
            ''')
            
            # Migration: Add 'type' column if it doesn't exist (for existing databases)
            cursor.execute("PRAGMA table_info(expenses)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'type' not in columns:
                print("Migrating database: Adding 'type' column to expenses table.")
                cursor.execute("ALTER TABLE expenses ADD COLUMN type TEXT DEFAULT 'Expense'")
                
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL UNIQUE,
                    limit_amount REAL NOT NULL
                )
            ''')
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Error initialising database: {e}")
        return False

def save_budget(category: str, limit: float) -> bool:
    """Save or update the budget limit for a specific category."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO budgets (category, limit_amount)
                VALUES (?, ?)
            ''', (category, float(limit)))
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Error saving budget: {e}")
        return False