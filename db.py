# db.py - Database connection, schema creation, and budget handling
import sqlite3
import os
import sys

def get_db_path():
    """Return the absolute path to the expenses.db file, safe for PyInstaller .exe."""
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe
        base = os.path.dirname(sys.executable)
    else:
        # Running as a normal .py script
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'expenses.db')

def get_connection():
    """Create and return a connection to expenses.db."""
    try:
        conn = sqlite3.connect(get_db_path())
        # Returning rows as dictionaries/tuples that support indexing by name
        conn.row_factory = sqlite3.Row 
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def initialise_db():
    """Create expenses and budgets tables if they do not exist."""
    conn = get_connection()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                note TEXT DEFAULT ''
            )
        ''')
        
        # Create budgets table
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
    finally:
        if conn:
            conn.close()

def save_budget(category, limit):
    """Save or update the budget limit for a specific category."""
    conn = get_connection()
    if conn is None:
        return False
        
    try:
        cursor = conn.cursor()
        # INSERT OR REPLACE handles both inserting new budgets and updating existing ones
        cursor.execute('''
            INSERT OR REPLACE INTO budgets (category, limit_amount)
            VALUES (?, ?)
        ''', (category, float(limit)))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error saving budget: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Quick test block
if __name__ == "__main__":
    print("--- Testing db.py ---")
    db_path = get_db_path()
    print(f"Database Path Target: {db_path}")
    
    print("\nInitialising DB and creating tables if missing...")
    success = initialise_db()
    if success:
        print(f"Success! Database ready.")
        print(f"File exists at path: {os.path.exists(db_path)}")
        
        print("\nTesting save_budget()...")
        save_success = save_budget("Food", 2500)
        print(f"Save 'Food' budget (2500): {'Success' if save_success else 'Failed'}")
    else:
        print("Failed to initialise database.")
