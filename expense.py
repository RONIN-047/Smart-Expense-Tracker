# expense.py - Core logic for adding, fetching, and deleting expenses
import sqlite3
import db
import utils

def add_expense(amount, category, date, note=''):
    # Insert a new expense into the database. Returns True on success
    conn = db.get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        # Parameterized query to prevent SQL injection
        cursor.execute('''
            INSERT INTO expenses (amount, category, date, note)
            VALUES (?, ?, ?, ?)
        ''', (float(amount), category, date, note))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error adding expense: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_expenses():
    # Return all expense rows as a list of tuples, ordered by date DESC.
    conn = db.get_connection()
    if conn is None:
        return []   
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses ORDER BY date DESC, id DESC')
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching expenses: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_expenses_by_category(category):
    # Return all expenses for a specific category.
    conn = db.get_connection()
    if conn is None:
        return []
    try:
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
    finally:
        if conn:
            conn.close()

def update_expense(expense_id, amount, category, date, note):
    """Update an existing expense in the database. Returns True on success."""
    conn = db.get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE expenses
            SET amount = ?, category = ?, date = ?, note = ?
            WHERE id = ?
        ''', (float(amount), category, date, note, expense_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error updating expense: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_expense(expense_id):
    # Delete the expense with the given ID. Returns True on success.
    conn = db.get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error deleting expense: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_categories():
    # Return a unique list of all categories used, combining database records with utils defaults.
    conn = db.get_connection()
    categories = list(utils.CATEGORIES) # Base defaults
    if not conn:
        return categories
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM expenses')
        for row in cursor.fetchall():
            if row['category'] not in categories:
                categories.append(row['category'])
        return categories
    except sqlite3.Error as e:
        print(f"Error fetching categories: {e}")
        return categories
    finally:
        if conn:
            conn.close()

# Quick test block
if __name__ == '__main__':
    print("--- Testing expense.py ---")    
    print("\n1. Adding sample expenses...")
    added1 = add_expense(150.0, "Food", "2026-04-11", "Lunch")
    added2 = add_expense(80.5, "Travel", "2026-04-10", "Bus")
    added3 = add_expense(500.0, "Shopping", utils.get_today(), "Shoes")
    print(f"Records Added: {added1}, {added2}, {added3}")
    print("\n2. Getting all expenses:")
    all_exp = get_all_expenses()
    for row in all_exp:
        print(f"ID: {row['id']} | {row['date']} | {row['category']} | Rs {row['amount']} | {row['note']}")
    print("\n3. Filtering by 'Food' category:")
    food_exp = get_expenses_by_category("Food")
    for row in food_exp:
        print(f"ID: {row['id']} | {row['date']} | Rs {row['amount']}")  
    print("\n4. Testing Deletion:")
    if all_exp:
        first_id = all_exp[0]['id']
        print(f"Deleting expense ID {first_id}...")
        del_success = delete_expense(first_id)
        print(f"Delete Submited: {del_success}")
        new_count = len(get_all_expenses())
        print(f"Expenses remaining: {new_count}")
