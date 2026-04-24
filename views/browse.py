# views/browse.py - Browse/filter all expenses with pagination for performance
import customtkinter as ctk
import tkinter.messagebox as messagebox
import datetime
import db
import expense
import analytics
import utils
from views.shared import *

PAGE_SIZE = 25  # Load 25 expenses at a time to prevent lag


class ViewExpensesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header with filter - OUTSIDE scroll area
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill='x', padx=30, pady=(30, 20))
        
        ctk.CTkLabel(header, text="Browse Expenses", font=("Arial", 32, "bold")).pack(side='left')
        
        filter_frame = ctk.CTkFrame(header, fg_color="transparent")
        filter_frame.pack(side='right')
        ctk.CTkLabel(filter_frame, text="Filter:", font=("Arial", 16), text_color="#888").pack(side='left', padx=(0, 15))
        self.var_filter = ctk.StringVar(value="All")
        self.cb = ctk.CTkComboBox(filter_frame, variable=self.var_filter, values=["All"], 
                                   command=self.load_expenses, state='readonly',
                                   width=200, height=40, font=("Arial", 14),
                                   fg_color=COLOR_SURFACE, border_color="#333344",
                                   button_color="#333344", button_hover_color="#444455")
        self.cb.pack(side='left')
        
        # Scrollable list - AT ROOT LEVEL with NO PADDING (scrollbar at left edge!)
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill='both', expand=True, padx=0, pady=(0, 20))
        
        # Bottom bar - OUTSIDE scroll area
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill='x', padx=30, pady=(0, 30))
        
        self.btn_load_more = ctk.CTkButton(bottom, text="Load More ↓", font=("Arial", 14, "bold"), 
                                            height=45, width=150, fg_color="#333344", hover_color="#444455",
                                            command=self._load_next_page)
        self.btn_load_more.pack(side='left')
        
        self.lbl_showing = ctk.CTkLabel(bottom, text="", font=("Arial", 14), text_color="#888")
        self.lbl_showing.pack(side='left', padx=20)
        
        self.lbl_total = ctk.CTkLabel(bottom, text="Total: Rs 0", font=("Arial", 24, "bold"), text_color=COLOR_PRIMARY)
        self.lbl_total.pack(side='right')
        
        # Pagination state
        self._all_expenses = []
        self._shown_count = 0
        
    def _render_date_group(self, date_str, expenses_in_group):
        """Render a date group header and its expenses"""
        # Parse date for display
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            today = datetime.datetime.now().date()
            expense_date = date_obj.date()
            
            if expense_date == today:
                date_display = f"📅 {date_obj.strftime('%B %d, %Y')} (Today)"
                date_color = COLOR_SUCCESS
            elif expense_date == today - datetime.timedelta(days=1):
                date_display = f"📅 {date_obj.strftime('%B %d, %Y')} (Yesterday)"
                date_color = COLOR_WARNING
            else:
                date_display = f"📅 {date_obj.strftime('%B %d, %Y')}"
                date_color = COLOR_PRIMARY
        except:
            date_display = f"📅 {date_str}"
            date_color = COLOR_PRIMARY
        
        # Date group container - WITH PADDING INSIDE
        group_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        group_frame.pack(fill='x', padx=30, pady=(0, 40))
        
        # Date header with background
        header_card = ctk.CTkFrame(group_frame, fg_color=COLOR_SURFACE, corner_radius=12, height=50)
        header_card.pack(fill='x', pady=(0, 15))
        header_card.pack_propagate(False)
        
        header_inner = ctk.CTkFrame(header_card, fg_color="transparent")
        header_inner.pack(fill='both', expand=True, padx=20, pady=12)
        
        ctk.CTkLabel(header_inner, text=date_display, font=("Arial", 18, "bold"), 
                    text_color=date_color).pack(side='left')
        
        # Count of expenses in this group
        count_text = f"{len(expenses_in_group)} expense{'s' if len(expenses_in_group) > 1 else ''}"
        ctk.CTkLabel(header_inner, text=count_text, font=("Arial", 14), 
                    text_color="#888").pack(side='right')
        
        # Render expenses in this group
        for idx, exp in enumerate(expenses_in_group):
            self._render_row(exp['id'], exp['category'], exp['amount'], exp['note'], idx, group_frame)
    
    def _render_row(self, exp_id, category, amount, note, idx, parent):
        """Render a single expense row - AMAZING with colors and hover!"""
        # Card with hover effect
        row = ctk.CTkFrame(parent, fg_color=COLOR_SURFACE, corner_radius=12, 
                          border_width=1, border_color="#333344")
        row.pack(fill='x', pady=6)
        
        # Bind hover effects
        def on_enter(e):
            row.configure(border_color="#555566")
        def on_leave(e):
            row.configure(border_color="#333344")
        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        
        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill='x', padx=20, pady=16)
        
        # Use grid for better control
        inner.grid_columnconfigure(1, weight=1)  # Note column expands
        
        # Category badge - USE LABEL NOT DISABLED BUTTON!
        cat_color = utils.get_category_color(category)
        cat_frame = ctk.CTkFrame(inner, fg_color=cat_color, corner_radius=15, height=34)
        cat_frame.grid(row=0, column=0, sticky='w', padx=(0, 20))
        cat_frame.pack_propagate(False)
        
        ctk.CTkLabel(cat_frame, text=utils.get_category_display(category), 
                    font=("Arial", 13, "bold"), text_color="#000000", width=130).pack(expand=True)
        
        # Note - expands to fill space, show only if exists
        if note and note.strip():
            ctk.CTkLabel(inner, text=note, font=("Arial", 14), 
                        text_color="#aaa", anchor='w').grid(row=0, column=1, sticky='ew', padx=(0, 20))
        else:
            # Empty space if no note
            ctk.CTkLabel(inner, text="", font=("Arial", 14)).grid(row=0, column=1, sticky='ew', padx=(0, 20))
        
        # Amount - fixed width, prominent
        ctk.CTkLabel(inner, text=utils.format_currency(amount), font=("Arial", 20, "bold"), 
                    text_color="white", width=150, anchor='e').grid(row=0, column=2, sticky='e', padx=(0, 20))
        
        # Delete button - more prominent
        ctk.CTkButton(inner, text="✕", width=40, height=34, fg_color="#2a1a1a", 
                     text_color=COLOR_DANGER, border_width=1, border_color=COLOR_DANGER,
                     hover_color="#3d1e1e", font=("Arial", 16, "bold"),
                     command=lambda: self._delete_expense(exp_id)).grid(row=0, column=3, sticky='e')

    def _group_expenses_by_date(self, expenses):
        """Group expenses by date"""
        groups = {}
        for exp in expenses:
            date = exp['date']
            if date not in groups:
                groups[date] = []
            groups[date].append(exp)
        return groups
    
    def _load_next_page(self):
        """Append the next batch of date groups without clearing existing ones."""
        start = self._shown_count
        end = min(start + PAGE_SIZE, len(self._all_expenses))
        
        # Get expenses for this page
        page_expenses = self._all_expenses[start:end]
        
        # Group by date
        page_groups = self._group_expenses_by_date(page_expenses)
        
        # Render each date group
        for date_str in sorted(page_groups.keys(), reverse=True):
            self._render_date_group(date_str, page_groups[date_str])
        
        self._shown_count = end
        self._update_status_bar()

    def _update_status_bar(self):
        total_count = len(self._all_expenses)
        if self._shown_count >= total_count:
            self.btn_load_more.pack_forget()
        else:
            self.btn_load_more.pack(side='left')
        self.lbl_showing.configure(text=f"Showing {self._shown_count} of {total_count}")

    def on_show(self):
        # Only reload if expense count changed since last visit
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('SELECT COUNT(*) as cnt FROM expenses')
                current_count = cur.fetchone()['cnt']
        except:
            current_count = -1

        if hasattr(self, '_last_expense_count') and self._last_expense_count == current_count:
            return
        self._last_expense_count = current_count

        cats = expense.get_all_categories()
        self.cb.configure(values=["All"] + cats)
        self.var_filter.set("All")
        self.load_expenses()
        
    def load_expenses(self, _=None):
        clear_frame(self.list_frame)
        cat = self.var_filter.get()
        self._all_expenses = expense.get_all_expenses() if cat == "All" else expense.get_expenses_by_category(cat)
        self._shown_count = 0

        if not self._all_expenses:
            # Empty state with icon - WITH PADDING
            empty_container = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            empty_container.pack(fill='x', padx=30)
            
            empty_frame = ctk.CTkFrame(empty_container, fg_color=COLOR_SURFACE, corner_radius=20)
            empty_frame.pack(pady=60, padx=40, fill='x')
            ctk.CTkLabel(empty_frame, text="📭", font=("Arial", 48)).pack(pady=(30, 10))
            ctk.CTkLabel(empty_frame, text="No expenses found", 
                        font=("Arial", 20, "bold")).pack(pady=(0, 5))
            ctk.CTkLabel(empty_frame, text="Try changing the filter or add a new expense", 
                        font=("Arial", 14), text_color="#888").pack(pady=(0, 30))
            self.lbl_total.configure(text="Total: Rs 0")
            self.btn_load_more.pack_forget()
            self.lbl_showing.configure(text="")
            return
            
        total = sum(e['amount'] for e in self._all_expenses)
        self.lbl_total.configure(text=f"Total: {utils.format_currency(total)}")
        
        # Load first page only
        self._load_next_page()
        
    def _delete_expense(self, exp_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense permanently?"):
            if expense.delete_expense(exp_id):
                analytics.invalidate_chart_cache()
                self.load_expenses()
