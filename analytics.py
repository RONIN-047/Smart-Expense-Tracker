# analytics.py - Calculates summaries, budget statuses, and generates visual charts
import sqlite3
import db
import utils
import matplotlib.pyplot as plt
import matplotlib
import datetime
from typing import List, Tuple, Any

matplotlib.use('TkAgg')

# --- Matplotlib Dark Theme Config ---
plt.style.use('dark_background')
BG_COLOR = '#2b2b2b' # Matches CustomTkinter dark theme

def get_category_summary() -> List[sqlite3.Row]:
    """Return list of rows ordered by total DESC."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, SUM(amount) as total 
                FROM expenses 
                GROUP BY category 
                ORDER BY total DESC
            ''')
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching category summary: {e}")
        return []

def get_monthly_summary() -> List[sqlite3.Row]:
    """Return list of rows ordered by month DESC."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT strftime('%Y-%m', date) as month_str, SUM(amount) as total 
                FROM expenses 
                GROUP BY month_str 
                ORDER BY month_str DESC
            ''')
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching monthly summary: {e}")
        return []

def get_budget_status() -> List[Tuple[str, float, float, str]]:
    """Return list of (category, limit, spent, status) tuples. Status is 'OK' or 'OVER!'."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            curr_month = datetime.datetime.now().strftime('%Y-%m') + '%'
            cursor.execute('''
                SELECT b.category, b.limit_amount, COALESCE(SUM(e.amount), 0) as spent
                FROM budgets b 
                LEFT JOIN expenses e ON b.category = e.category AND e.date LIKE ?
                WHERE b.category != 'GLOBAL_TOTAL'
                GROUP BY b.category
            ''', (curr_month,))   
            results: List[Tuple[str, float, float, str]] = []
            for row in cursor.fetchall():
                cat = row['category']
                limit = row['limit_amount']
                spent = row['spent']
                status = 'OVER!' if spent > limit else 'OK'
                results.append((cat, limit, spent, status)) 
                
            # Add GLOBAL_TOTAL if it exists
            cursor.execute("SELECT limit_amount FROM budgets WHERE category = 'GLOBAL_TOTAL'")
            global_budget = cursor.fetchone()
            if global_budget:
                cursor.execute("SELECT SUM(amount) as spent FROM expenses WHERE date LIKE ?", (curr_month,))
                global_spent = cursor.fetchone()['spent'] or 0
                limit = global_budget['limit_amount']
                status = 'OVER!' if global_spent > limit else 'OK'
                results.append(('GLOBAL_TOTAL', limit, global_spent, status))
                
            return results
    except sqlite3.Error as e:
        print(f"Error fetching budget status: {e}")
        return []

def get_category_bar_chart_figure() -> Any:
    """Generate and return a matplotlib figure for category totals."""
    data = get_category_summary()
    if not data:
        return None    
    categories = [row['category'] for row in data]
    totals = [row['total'] for row in data]
    fig, ax = plt.subplots(figsize=(5, 4))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    bars = plt.barh(categories, totals, color='#3b8ed0')
    plt.xlabel('Total Amount (Rs)', color='lightgrey', fontsize=12)
    plt.title('Category-wise Spending (Bar)', color='white', fontsize=15, pad=15)
    plt.gca().invert_yaxis()   
    for bar in bars:
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2, f' Rs {width:,.0f}', 
                 ha='left', va='center', fontsize=11, color='white')              
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#555555')
    ax.spines['left'].set_color('#555555')
    ax.tick_params(colors='lightgrey', labelsize=11)
    plt.close(fig) # close it from aggressive rendering
    return fig

def get_category_pie_chart_figure() -> Any:
    """Generate and return a matplotlib figure for category proportions."""
    data = get_category_summary()
    if not data:
        return None
    categories = [row['category'] for row in data]
    totals = [row['total'] for row in data]    
    fig, ax = plt.subplots(figsize=(5, 4))
    fig.patch.set_facecolor(BG_COLOR)    
    colors = ['#3b8ed0', '#2fa572', '#eaaa00', '#d35b5b', '#8a6f9c', '#5fd3b3', '#dc8a3d', '#70a5d3']
    wedges, texts, autotexts = plt.pie(totals, labels=categories, autopct='%1.1f%%', 
                                       startangle=140, colors=colors, textprops=dict(color="w")) 
    plt.setp(autotexts, size=11, weight="bold")
    plt.setp(texts, size=12)                               
    plt.title('Spending Proportions (Pie)', color='white', fontsize=15, pad=15)
    plt.axis('equal') 
    plt.close(fig)
    return fig

def get_monthly_trend_figure() -> Any:
    """Generate and return a matplotlib figure for monthly spending trend."""
    data = get_monthly_summary()
    if not data:
        return None
    data = list(reversed(data))
    months = [utils.format_month(row['month_str']) for row in data]
    totals = [row['total'] for row in data]
    fig, ax = plt.subplots(figsize=(8, 3))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    plt.plot(months, totals, marker='o', linestyle='-', color='#eaaa00', linewidth=2, markersize=6)
    plt.fill_between(months, totals, alpha=0.15, color='#eaaa00')
    
    # Add budget line
    budget_status = get_budget_status()
    global_total_limit = next((row[1] for row in budget_status if row[0] == 'GLOBAL_TOTAL'), None)
    
    if global_total_limit:
        plt.axhline(y=global_total_limit, color='#d35b5b', linestyle='--', linewidth=1.5, alpha=0.8)
        ax.text(0, global_total_limit, ' Monthly Budget', color='#d35b5b', va='bottom', ha='left', fontsize=10, weight='bold')

    max_val = max(totals) if totals else 0
    if global_total_limit and global_total_limit > max_val:
        max_val = global_total_limit
        
    ax.set_ylim(top=max_val * 1.25) # Add top padding to prevent peak cutoff
    plt.ylabel('Total Amount (Rs)', color='lightgrey', fontsize=13)
    plt.title('Monthly Spending Trend', color='white', fontsize=16, pad=15)
    plt.grid(True, linestyle='--', alpha=0.2, color='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#555555')
    ax.spines['left'].set_color('#555555')
    ax.tick_params(colors='lightgrey', labelsize=12)
    for i, total in enumerate(totals):
        plt.text(i, total + (max(totals)*0.05), f'Rs {total:,.0f}', ha='center', va='bottom', color='white', weight='bold', fontsize=13)
    plt.xticks(rotation=15)
    plt.close(fig)
    return fig