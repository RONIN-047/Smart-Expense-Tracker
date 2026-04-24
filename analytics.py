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
BG_COLOR = '#0f0f1a' # Deep navy for graphs
SURFACE_COLOR = '#16213e' # Matches new CustomTkinter surfaces

# --- Chart Cache (reduces lag on repeated tab switches) ---
_chart_cache = {}
_last_expense_count = -1  # Track if data changed

def _data_changed() -> bool:
    """Check if expense data has changed since last chart generation."""
    global _last_expense_count
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as cnt FROM expenses')
            count = cursor.fetchone()['cnt']
            if count != _last_expense_count:
                _last_expense_count = count
                _chart_cache.clear()
                return True
            return False
    except:
        return True

def invalidate_chart_cache():
    """Force charts to regenerate on next request."""
    global _last_expense_count
    _last_expense_count = -1
    _chart_cache.clear()

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
    _data_changed()  # Check for cache invalidation
    if 'bar' in _chart_cache:
        return _chart_cache['bar']
    
    data = get_category_summary()
    if not data:
        return None    
    categories = [row['category'] for row in data]
    totals = [row['total'] for row in data]
    fig, ax = plt.subplots(figsize=(6, 4.5))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    colors = [utils.get_category_color(cat) for cat in categories]
    y_positions = range(len(categories))
    bars = ax.barh(y_positions, totals, color=colors, height=0.6)
    ax.set_yticks([])
    ax.set_xlabel('Total Amount (Rs)', color='lightgrey', fontsize=13)
    ax.set_title('Category Spending', color='white', fontsize=17, weight='bold', pad=15)
    ax.invert_yaxis()
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, f' Rs {width:,.0f}', 
                ha='left', va='center', fontsize=12, color='white', weight='bold')              
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#333344')
    ax.spines['left'].set_color('#333344')
    ax.tick_params(colors='lightgrey', labelsize=12)
    # Add a legend with category names and colors
    legend_handles = [plt.Rectangle((0,0),1,1, fc=c) for c in colors]
    ax.legend(legend_handles, categories, loc='lower right', fontsize=11,
             facecolor=SURFACE_COLOR, edgecolor='#333344', labelcolor='white',
             framealpha=0.9)
    fig.tight_layout()
    plt.close(fig)
    _chart_cache['bar'] = fig
    return fig

def get_category_pie_chart_figure() -> Any:
    """Generate and return a matplotlib figure for category proportions."""
    _data_changed()
    if 'pie' in _chart_cache:
        return _chart_cache['pie']
    
    data = get_category_summary()
    if not data:
        return None
    categories = [row['category'] for row in data]
    totals = [row['total'] for row in data]
    grand_total = sum(totals)
    
    fig, ax = plt.subplots(figsize=(6, 4.5))
    fig.patch.set_facecolor(BG_COLOR)    
    colors = [utils.get_category_color(cat) for cat in categories]
    
    # Custom autopct: hide percentage text for slices smaller than 5%
    def smart_autopct(pct):
        return f'{pct:.1f}%' if pct >= 5 else ''
    
    wedges, texts, autotexts = ax.pie(totals, labels=None, autopct=smart_autopct, 
                                      startangle=140, colors=colors, textprops=dict(color="w"),
                                      wedgeprops=dict(width=0.4, edgecolor=BG_COLOR, linewidth=2),
                                      pctdistance=0.78)
    plt.setp(autotexts, size=12, weight="bold")
    ax.set_title('Spending Proportions', color='white', fontsize=17, weight='bold', pad=15)
    
    # Add a center circle for the donut effect
    center_circle = plt.Circle((0,0), 0.55, fc=BG_COLOR)
    ax.add_artist(center_circle)
    
    # Legend with category names, color boxes, and percentages for small slices
    legend_labels = []
    for cat, total in zip(categories, totals):
        pct = (total / grand_total) * 100 if grand_total > 0 else 0
        if pct < 5:
            legend_labels.append(f'{cat} ({pct:.1f}%)')
        else:
            legend_labels.append(cat)
    
    ax.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(0.88, 0.5), fontsize=11,
             facecolor=SURFACE_COLOR, edgecolor='#333344', labelcolor='white',
             framealpha=0.9)
    
    ax.axis('equal') 
    fig.tight_layout()
    plt.close(fig)
    _chart_cache['pie'] = fig
    return fig

def get_monthly_trend_figure() -> Any:
    """Generate and return a matplotlib figure for monthly spending trend."""
    _data_changed()
    if 'trend' in _chart_cache:
        return _chart_cache['trend']
    
    data = get_monthly_summary()
    if not data:
        return None
    data = list(reversed(data))
    months = [utils.format_month(row['month_str']) for row in data]
    totals = [row['total'] for row in data]

    fig, ax = plt.subplots(figsize=(8, 3.5))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    # Always use smooth line + gradient fill (Option 1 style)
    # For single data point, pad with a zero so the line/fill renders
    if len(totals) == 1:
        plot_months = ['', months[0], '']
        plot_totals = [0, totals[0], totals[0]]
    else:
        plot_months = months
        plot_totals = totals

    # Gradient fill under the line
    from matplotlib.patches import Polygon
    import numpy as np
    xs = np.arange(len(plot_months))
    ax.plot(xs, plot_totals, color='#00d2ff', linewidth=3,
            marker='o', markersize=8, markerfacecolor='#00d2ff',
            markeredgecolor='#0a0a1a', markeredgewidth=2, zorder=3)

    # Gradient fill using imshow trick
    ax.fill_between(xs, plot_totals, alpha=0, color='#00d2ff')  # invisible, just for extent
    gradient_steps = 200
    max_y = max(plot_totals) * 1.35 if plot_totals else 1
    for i in range(len(xs) - 1):
        x0, x1 = xs[i], xs[i + 1]
        y0, y1 = plot_totals[i], plot_totals[i + 1]
        verts = [(x0, 0), (x0, y0), (x1, y1), (x1, 0)]
        poly = Polygon(verts, facecolor='#00d2ff', alpha=0.18, zorder=1)
        ax.add_patch(poly)

    # Value labels above each real data point
    real_xs = xs[1:-1] if len(totals) == 1 else xs
    real_totals = totals
    for i, (x, total) in enumerate(zip(real_xs, real_totals)):
        ax.text(x, total + max(real_totals) * 0.06,
                f'Rs {total:,.0f}',
                ha='center', va='bottom', color='#00d2ff',
                weight='bold', fontsize=11,
                bbox=dict(facecolor=SURFACE_COLOR, edgecolor='none',
                          alpha=0.8, boxstyle='round,pad=0.3'))

    ax.set_xticks(xs)
    ax.set_xticklabels(plot_months, rotation=0, ha='center')

    # Budget line - only if within 3x of max data
    budget_status = get_budget_status()
    global_total_limit = next((row[1] for row in budget_status if row[0] == 'GLOBAL_TOTAL'), None)
    max_data = max(plot_totals) if plot_totals else 1

    if global_total_limit and global_total_limit <= max_data * 3:
        ax.axhline(y=global_total_limit, color='#ff6b6b', linestyle='--',
                   linewidth=1.5, alpha=0.8, zorder=2)
        ax.text(xs[0], global_total_limit, '  Budget Limit',
                color='#ff6b6b', va='bottom', ha='left', fontsize=11, weight='bold')
        y_top = max(max_data, global_total_limit) * 1.35
    else:
        y_top = max_data * 1.35

    ax.set_ylim(bottom=0, top=y_top)
    ax.set_xlim(left=-0.5, right=len(plot_months) - 0.5)
    ax.set_ylabel('Total (Rs)', color='lightgrey', fontsize=12)
    ax.set_title('Monthly Spending Trend', color='white', fontsize=16, weight='bold', pad=15)
    ax.grid(True, linestyle='--', alpha=0.1, color='white', zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#333344')
    ax.spines['left'].set_color('#333344')
    ax.tick_params(colors='lightgrey', labelsize=12)
    fig.tight_layout()
    plt.close(fig)
    _chart_cache['trend'] = fig
    return fig