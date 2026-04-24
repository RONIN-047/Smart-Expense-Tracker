# views/dashboard.py - Home dashboard with summary cards, recent transactions, budget bar, and charts
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import db
import expense
import analytics
import utils
from views.shared import *


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Make the whole dashboard scrollable with MORE padding
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill='both', expand=True, padx=30, pady=30)  # Increased padding
        
        # Welcome Header - MUCH more breathing room
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill='x', pady=(0, 50))
        
        # Top line: Greeting on left, Balance on right
        top_line = ctk.CTkFrame(header, fg_color="transparent")
        top_line.pack(fill='x', anchor='n')
        
        now = datetime.datetime.now()
        greeting = "Good Evening 🌙"
        if now.hour < 12: greeting = "Good Morning ☀️"
        elif now.hour < 17: greeting = "Good Afternoon 🌤️"
        
        greeting_label = ctk.CTkLabel(top_line, text=greeting, font=("Arial", 40, "bold"))
        greeting_label.pack(side='left')
        
        self.val_balance_top = ctk.StringVar(value="Balance: Rs 0")
        self.lbl_balance_top = ctk.CTkLabel(top_line, textvariable=self.val_balance_top, font=("Arial", 32, "bold"), text_color=COLOR_PRIMARY)
        self.lbl_balance_top.pack(side='right')
        
        # Date label below greeting
        date_label = ctk.CTkLabel(header, text=now.strftime('%A, %b %d, %Y'), font=("Arial", 16), text_color="grey")
        date_label.pack(anchor='w', pady=(5, 0))
        
        # Summary Cards Row - MUCH better spacing
        cards_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        cards_frame.pack(fill='x', pady=(0, 50))
        self.val_total_exp = ctk.StringVar(value="Rs 0")
        self.val_month_exp = ctk.StringVar(value="Rs 0")
        self.val_month_inc = ctk.StringVar(value="Rs 0")
        
        self._create_summary_card(cards_frame, "Monthly Income", self.val_month_inc, COLOR_SUCCESS, "📈", "#006400", "#00d2ff").pack(side='right', fill='x', expand=True, padx=(20, 0))
        self._create_summary_card(cards_frame, "Monthly Expenses", self.val_month_exp, COLOR_DANGER, "📉", "#8b0000", "#ff6b6b").pack(side='right', fill='x', expand=True, padx=20)
        self._create_summary_card(cards_frame, "Total Expenses", self.val_total_exp, COLOR_PRIMARY, "💰", "#1a1a2e", "#00d2ff").pack(side='right', fill='x', expand=True, padx=(0, 20))
        
        # Recent Transactions Section - ALIGNED with cards
        section_label = ctk.CTkLabel(self.scroll, text="Recent Transactions", font=("Arial", 24, "bold"))
        section_label.pack(anchor='w', pady=(0, 20), padx=10)  # Added padx to align with cards!
        self.recent_cards_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.recent_cards_frame.pack(fill='x', pady=(0, 60))  # EVEN MORE space after
        self.recent_cards_frame.grid_columnconfigure(0, weight=1)
        self.recent_cards_frame.grid_columnconfigure(1, weight=1)
        self.recent_cards_frame.grid_columnconfigure(2, weight=1)
        
        # Monthly Budget Section - ALIGNED
        budget_label = ctk.CTkLabel(self.scroll, text="Monthly Budget", font=("Arial", 24, "bold"))
        budget_label.pack(anchor='w', pady=(0, 20), padx=10)  # Added padx to align!
        self.budget_section = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.budget_section.pack(fill='x', pady=(0, 60))  # EVEN MORE space after
        
        # Charts Section - ALIGNED
        charts_label = ctk.CTkLabel(self.scroll, text="Expenditure Insights", font=("Arial", 24, "bold"))
        charts_label.pack(anchor='w', pady=(0, 20), padx=10)  # Added padx to align!
        self.charts_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.charts_frame.pack(fill='both', expand=True, pady=(0, 30))

    def _create_summary_card(self, parent, title, var, text_color, icon, gradient_start, gradient_end):
        """Create gradient summary card - BIGGER with proper text spacing"""
        frame = ctk.CTkFrame(parent, corner_radius=20, fg_color=gradient_start, border_width=0)
        frame.pack_propagate(False)
        frame.configure(height=220)  # Even taller to fit text properly!
        
        # Content with LOTS of padding
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill='both', expand=True, padx=40, pady=40)  # More vertical padding
        
        # Icon with proper spacing
        icon_label = ctk.CTkLabel(content, text=icon, font=("Arial", 48))
        icon_label.pack(anchor='w', pady=(0, 8))
        
        # Title with proper spacing
        title_label = ctk.CTkLabel(content, text=title, font=("Arial", 17), text_color="white")
        title_label.pack(anchor='w', pady=(0, 8))
        
        # Value with EXTRA height to prevent clipping
        lbl_val = ctk.CTkLabel(content, textvariable=var, font=("Arial", 36, "bold"), text_color="white", height=50)  # Added explicit height!
        lbl_val.pack(anchor='w', pady=(0, 0))
        
        frame._lbl_val = lbl_val
        return frame
    
    def _render_recent_card(self, col, date, category, amount, note):
        """Render recent transaction with side icon box - spacious and polished"""
        cat_color = utils.get_category_color(category)
        card = ctk.CTkFrame(self.recent_cards_frame, fg_color=COLOR_SURFACE, corner_radius=18, 
                            border_width=1, border_color="#333344", height=160)  # More height
        card.grid(row=0, column=col, sticky='nsew', padx=10, pady=5)  # Better horizontal spacing
        card.pack_propagate(False)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill='both', expand=True, padx=25, pady=22)  # More padding
        
        # Horizontal layout with icon box on left
        layout = ctk.CTkFrame(inner, fg_color="transparent")
        layout.pack(fill='both', expand=True)
        
        # Icon box - bigger and better proportioned
        icon_box = ctk.CTkFrame(layout, width=65, height=65, fg_color=cat_color, corner_radius=14)
        icon_box.pack(side='left', padx=(0, 20))  # More spacing from content
        icon_box.pack_propagate(False)
        icon_text = utils.get_category_display(category).split()[0]  # Get just the emoji
        ctk.CTkLabel(icon_box, text=icon_text, font=("Arial", 30)).pack(expand=True)
        
        # Content on right
        content = ctk.CTkFrame(layout, fg_color="transparent")
        content.pack(side='left', fill='both', expand=True)
        
        # Top row: category name and date
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill='x')
        ctk.CTkLabel(top_row, text=category, font=("Arial", 16, "bold"), 
                    text_color=cat_color).pack(side='left')
        ctk.CTkLabel(top_row, text=date[-5:], font=("Arial", 14), 
                    text_color="#888").pack(side='right')
        
        # Amount - bigger and more prominent
        ctk.CTkLabel(content, text=amount, font=("Arial", 28, "bold"), 
                    text_color="white").pack(anchor='w', pady=(10, 8))
        
        # Note
        display_note = note if note else "—"
        ctk.CTkLabel(content, text=display_note, font=("Arial", 14), 
                    text_color="#aaa", anchor='w').pack(anchor='w')

    def _render_budget_summary(self):
        """Render budget bar - FULL WIDTH and prominent"""
        clear_frame(self.budget_section)
        budgets = analytics.get_budget_status()
        global_row = next((r for r in budgets if r[0] == 'GLOBAL_TOTAL'), None)
        if not global_row:
            return
        cat, limit, spent, status = global_row
        is_over = (status == 'OVER!')
        prog_val = min(spent / limit if limit > 0 else 0, 1.0)
        
        # Card with full width
        inner = ctk.CTkFrame(self.budget_section, fg_color=COLOR_SURFACE, corner_radius=20, border_width=1, border_color="#333344")
        inner.pack(fill='both', expand=True)  # FILL BOTH
        
        content = ctk.CTkFrame(inner, fg_color="transparent")
        content.pack(fill='both', expand=True, padx=40, pady=35)  # Lots of padding
        
        # Header
        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill='x', pady=(0, 20))
        status_text = f"{utils.format_currency(spent)} / {utils.format_currency(limit)}"
        ctk.CTkLabel(top, text=status_text, font=("Arial", 18, "bold"), 
                    text_color="#aaa").pack(side='right')
        
        # Progress bar - BIGGER and FULL WIDTH
        if is_over:
            bar_color = COLOR_DANGER
        elif prog_val > 0.85:
            bar_color = COLOR_WARNING
        else:
            bar_color = COLOR_SUCCESS
            
        progress = ctk.CTkProgressBar(content, height=45, progress_color=bar_color, corner_radius=22)  # Even taller!
        progress.pack(fill='x', pady=(0, 18))  # FILL X
        progress.set(prog_val)
        
        # Bottom row
        bottom = ctk.CTkFrame(content, fg_color="transparent")
        bottom.pack(fill='x')
        
        percentage_text = f"{int(prog_val * 100)}% used"
        ctk.CTkLabel(bottom, text=percentage_text, font=("Arial", 17, "bold"), 
                    text_color=bar_color).pack(side='left')
        
        remaining = limit - spent
        if remaining > 0:
            ctk.CTkLabel(bottom, text=f"{utils.format_currency(remaining)} remaining", 
                        font=("Arial", 17, "bold"), text_color=COLOR_SUCCESS).pack(side='right')
        
        if is_over:
            ctk.CTkLabel(content, text="⚠️ Over budget!", font=("Arial", 17, "bold"), 
                        text_color=COLOR_DANGER).pack(anchor='w', pady=(12, 0))

    def force_refresh(self):
        """Force a full reload on next on_show() call (e.g. after budget changes)."""
        self._last_expense_count = -1
        self._last_budget_hash = -1

    def on_show(self):
        # Only reload if expense count or budget limits changed since last visit
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('SELECT COUNT(*) as cnt FROM expenses')
                current_count = cur.fetchone()['cnt']
                cur.execute('SELECT category, limit_amount FROM budgets ORDER BY category')
                budget_hash = hash(tuple((r['category'], r['limit_amount']) for r in cur.fetchall()))
        except:
            current_count = -1
            budget_hash = -1

        if (hasattr(self, '_last_expense_count') and self._last_expense_count == current_count
                and hasattr(self, '_last_budget_hash') and self._last_budget_hash == budget_hash):
            return
        self._last_expense_count = current_count
        self._last_budget_hash = budget_hash

        expenses = expense.get_all_expenses()
        balance = analytics.get_total_balance()
        total_exp = sum(e['amount'] for e in expenses if e['type'] == 'Expense')
        curr_month = datetime.datetime.now().strftime('%Y-%m')
        month_exp = sum(e['amount'] for e in expenses if e['date'].startswith(curr_month) and e['type'] == 'Expense')
        month_inc = analytics.get_monthly_income(curr_month)
        
        self.val_total_exp.set(utils.format_currency(total_exp))
        self.val_balance_top.set(f"Balance: {utils.format_currency(balance)}")
        self.val_month_inc.set(utils.format_currency(month_inc))
        self.val_month_exp.set(utils.format_currency(month_exp))
        
        # Budget warning sidebar highlight
        budgets = analytics.get_budget_status()
        warnings = sum(1 for b in budgets if b[3] == 'OVER!')
        if hasattr(self.winfo_toplevel(), 'update_sidebar_budget_warning'):
            self.winfo_toplevel().update_sidebar_budget_warning(warnings)
        
        # Render 3 recent transactions
        clear_frame(self.recent_cards_frame)
        self.recent_cards_frame.grid_columnconfigure(0, weight=1)
        self.recent_cards_frame.grid_columnconfigure(1, weight=1)
        self.recent_cards_frame.grid_columnconfigure(2, weight=1)
        if expenses:
            for i, e in enumerate(expenses[:3]):
                self._render_recent_card(i, e['date'], e['category'], utils.format_currency(e['amount']), e['note'])
        else:
            ctk.CTkLabel(self.recent_cards_frame, text="No expenses yet. Add your first one!", text_color="grey", font=("Arial", 16)).grid(row=0, column=0, columnspan=3, pady=50)
        
        self._render_budget_summary()
            
        # Draw Charts stacked vertically with better spacing
        clear_frame(self.charts_frame)
        
        if not expenses:
            ctk.CTkLabel(self.charts_frame, text="Log expenses to generate insights.", 
                        text_color="grey", font=("Arial", 16)).pack(pady=50)
            return
        
        # Pie Chart with better spacing
        try:
            fig_pie = analytics.get_category_pie_chart_figure()
            if fig_pie:
                pie_card = ctk.CTkFrame(self.charts_frame, fg_color=COLOR_SURFACE, corner_radius=18, 
                                       border_width=1, border_color="#333344")
                pie_card.pack(fill='both', expand=True, pady=(0, 20))  # More space between charts
                
                ctk.CTkLabel(pie_card, text="📊 Spending by Category", 
                            font=("Arial", 22, "bold"), text_color=COLOR_PRIMARY).pack(anchor='w', padx=30, pady=(25, 12))
                
                canvas_pie = FigureCanvasTkAgg(fig_pie, master=pie_card)
                canvas_pie.draw()
                canvas_pie.get_tk_widget().pack(fill='both', expand=True, padx=15, pady=(0, 15))
        except Exception as e:
            print(f"Error generating pie chart: {e}")
            error_card = ctk.CTkFrame(self.charts_frame, fg_color=COLOR_SURFACE, corner_radius=18, 
                                     border_width=1, border_color="#333344", height=380)
            error_card.pack(fill='x', pady=(0, 20))
            error_card.pack_propagate(False)
            ctk.CTkLabel(error_card, text="📊 Spending by Category", 
                        font=("Arial", 22, "bold"), text_color=COLOR_PRIMARY).pack(anchor='w', padx=30, pady=(25, 12))
            ctk.CTkLabel(error_card, text="Chart unavailable", text_color="grey", 
                        font=("Arial", 14)).pack(expand=True)
        
        # Bar Chart
        try:
            fig_bar = analytics.get_category_bar_chart_figure()
            if fig_bar:
                bar_card = ctk.CTkFrame(self.charts_frame, fg_color=COLOR_SURFACE, corner_radius=18,
                                       border_width=1, border_color="#333344")
                bar_card.pack(fill='both', expand=True, pady=(0, 20))
                ctk.CTkLabel(bar_card, text="📈 Category Breakdown",
                            font=("Arial", 22, "bold"), text_color=COLOR_PRIMARY).pack(anchor='w', padx=30, pady=(25, 12))
                canvas_bar = FigureCanvasTkAgg(fig_bar, master=bar_card)
                canvas_bar.draw()
                canvas_bar.get_tk_widget().pack(fill='both', expand=True, padx=15, pady=(0, 15))
        except Exception as e:
            print(f"Error generating bar chart: {e}")
            error_card = ctk.CTkFrame(self.charts_frame, fg_color=COLOR_SURFACE, corner_radius=18,
                                     border_width=1, border_color="#333344", height=380)
            error_card.pack(fill='x', pady=(0, 20))
            error_card.pack_propagate(False)
            ctk.CTkLabel(error_card, text="📈 Category Breakdown",
                        font=("Arial", 22, "bold"), text_color=COLOR_PRIMARY).pack(anchor='w', padx=30, pady=(25, 12))
            ctk.CTkLabel(error_card, text="Chart unavailable", text_color="grey",
                        font=("Arial", 14)).pack(expand=True)
