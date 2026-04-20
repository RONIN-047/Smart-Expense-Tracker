import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import db
import expense
import analytics
import tkcalendar
import utils
import datetime
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

WINDOW_WIDTH = 1350
WINDOW_HEIGHT = 850
COLOR_SUCCESS = '#2fa572'
COLOR_WARNING = '#eaaa00'
COLOR_DANGER = '#d35b5b'
COLOR_SURFACE = '#2b2b2b'

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def show_auto_dismiss_message(label, text, color, delay=3000):
    label.configure(text=text, text_color=color)
    if hasattr(label, '_timer') and label._timer:
        label.after_cancel(label._timer)
    label._timer = label.after(delay, lambda: label.configure(text=""))

# --- Individual Application Views ---

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        ctk.CTkLabel(self, text="Home Dashboard", font=ctk.CTkFont(size=30, weight="bold")).pack(anchor='w', pady=(0, 20))
        
        # Summary Cards
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill='x', pady=(0, 15))
        self.val_total = ctk.StringVar(value="Rs 0")
        self.val_month = ctk.StringVar(value="Rs 0")
        self.val_warn  = ctk.StringVar(value="0")
        self.card_warn_obj = self.create_card(cards_frame, "Active Warnings", self.val_warn, COLOR_SUCCESS)
        self.btn_view_budgets = ctk.CTkButton(
            self.card_warn_obj, text="View Budgets", width=100, height=24, 
            font=ctk.CTkFont(size=11, weight="bold"), fg_color=COLOR_DANGER, 
            hover_color="#9e4343", command=lambda: self.winfo_toplevel().show_frame("Budget")
        )
        self.card_warn_obj.pack(side='right', fill='x', expand=True, padx=(10, 0))
        self.create_card(cards_frame, "This Month", self.val_month, "#3b8ed0").pack(side='right', fill='x', expand=True, padx=10)
        self.create_card(cards_frame, "Total Expenses", self.val_total, "#3b8ed0").pack(side='right', fill='x', expand=True, padx=(0, 10))
        
        # Split Layout for Sidebar and Charts
        split_frame = ctk.CTkFrame(self, fg_color="transparent")
        split_frame.pack(fill='both', expand=True)
        split_frame.grid_columnconfigure(0, weight=1)
        split_frame.grid_columnconfigure(1, weight=1)
        split_frame.grid_rowconfigure(0, weight=1)
        
        # Left Side
        left_col = ctk.CTkFrame(split_frame, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky='nsew', padx=(0,10))
        ctk.CTkLabel(left_col, text="Recent Expenses", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor='w', pady=(10, 10))
        self.list_frame = ctk.CTkScrollableFrame(left_col, fg_color=COLOR_SURFACE, corner_radius=15)
        self.list_frame.pack(fill='both', expand=True)
        
        # Right Side (Charts)
        right_col = ctk.CTkFrame(split_frame, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky='nsew', padx=(10,0))
        ctk.CTkLabel(right_col, text="Expenditure Insights", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor='w', pady=(10, 10))
        self.charts_frame = ctk.CTkScrollableFrame(right_col, fg_color=COLOR_SURFACE, corner_radius=15)
        self.charts_frame.pack(fill='both', expand=True)

    def create_card(self, parent, title, var, text_color):
        frame = ctk.CTkFrame(parent, fg_color=COLOR_SURFACE, corner_radius=15)
        frame.pack_propagate(False)
        frame.configure(height=100)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14), text_color="grey").pack(anchor='nw', padx=15, pady=(15, 5))
        lbl_val = ctk.CTkLabel(frame, textvariable=var, font=ctk.CTkFont(size=24, weight="bold"), text_color=text_color)
        lbl_val.pack(anchor='nw', padx=15)
        return frame
        
    def render_row(self, date, category, amount, note):
        row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        row.pack(fill='x', pady=8, padx=10)
        
        ctk.CTkLabel(row, text=date, font=ctk.CTkFont(size=12, weight="bold"), width=90, anchor='w').pack(side='left')
        
        cat_badge = ctk.CTkFrame(row, fg_color="#3b8ed0", corner_radius=10, height=25)
        cat_badge.pack(side='left', padx=10)
        cat_badge.pack_propagate(False)
        display_cat = utils.get_category_display(category)
        ctk.CTkLabel(cat_badge, text=display_cat, font=ctk.CTkFont(size=12, weight="bold"), text_color="white", width=110).pack(expand=True)
        
        ctk.CTkLabel(row, text=note, font=ctk.CTkFont(size=13), text_color="grey", anchor='w').pack(side='left', fill='x', expand=True, padx=10)
        ctk.CTkLabel(row, text=amount, font=ctk.CTkFont(size=14, weight="bold")).pack(side='right')

    def on_show(self):
        expenses = expense.get_all_expenses()
        total_exp = sum(e['amount'] for e in expenses)
        self.val_total.set(utils.format_currency(total_exp))
        
        curr_month = datetime.datetime.now().strftime('%Y-%m')
        month_exp = sum(e['amount'] for e in expenses if e['date'].startswith(curr_month))
        self.val_month.set(utils.format_currency(month_exp))
        
        budgets = analytics.get_budget_status()
        warnings = sum(1 for b in budgets if b[3] == 'OVER!')
        self.val_warn.set(str(warnings))
        
        lbl_obj = self.card_warn_obj.winfo_children()[1]
        lbl_obj.configure(text_color=COLOR_DANGER if warnings > 0 else COLOR_SUCCESS)
        
        if warnings > 0:
            self.btn_view_budgets.place(relx=0.95, rely=0.15, anchor='ne')
        else:
            self.btn_view_budgets.place_forget()
            
        clear_frame(self.list_frame)
        for e in expenses[:10]:
            self.render_row(e['date'], e['category'], utils.format_currency(e['amount']), e['note'])
            
        if not expenses:
            ctk.CTkLabel(self.list_frame, text="No expenses found. Let's add one!", text_color="grey").pack(pady=40)
            
        # Draw Charts on Dashboard!
        clear_frame(self.charts_frame)
        fig_pie = analytics.get_category_pie_chart_figure()
        if fig_pie:
            canvas_pie = FigureCanvasTkAgg(fig_pie, master=self.charts_frame)
            canvas_pie.draw()
            canvas_pie.get_tk_widget().pack(side='top', fill='both', expand=True, pady=(0, 15))
            
        fig_bar = analytics.get_category_bar_chart_figure()
        if fig_bar:
            canvas_bar = FigureCanvasTkAgg(fig_bar, master=self.charts_frame)
            canvas_bar.draw()
            canvas_bar.get_tk_widget().pack(side='top', fill='both', expand=True, pady=(0, 15))
        elif not fig_pie:
            ctk.CTkLabel(self.charts_frame, text="Log expenses to generate insights.", text_color="grey").pack(pady=40)

class AddExpenseFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        ctk.CTkLabel(self, text="Add New Expense", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor='w', pady=(0, 20))
        card = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=15)
        card.pack(fill='both', expand=True)
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(pady=40, padx=40, anchor='nw', fill='both', expand=True)
        form.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(form, text="Amount (Rs)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky='w', pady=(0,5))
        self.ent_amount = ctk.CTkEntry(form, width=350, height=40, placeholder_text="e.g. 1500")
        self.ent_amount.grid(row=1, column=0, sticky='w', pady=(0,20))
        
        ctk.CTkLabel(form, text="Category Tags", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky='w', pady=(0,5))
        self.tags_frame = ctk.CTkFrame(form, height=50, fg_color="transparent")
        self.tags_frame.grid(row=3, column=0, sticky='ew', pady=(0, 10))
        self.selected_tag = ctk.StringVar(value="")
        self.bubble_buttons = []
        self.ent_custom_tag = ctk.CTkEntry(form, width=350, height=40, placeholder_text="Type custom tag...")       #Custom Tags
        
        ctk.CTkLabel(form, text="Date (YYYY-MM-DD)", font=ctk.CTkFont(weight="bold")).grid(row=5, column=0, sticky='w', pady=(0,5))
        self.selected_date = ctk.StringVar(value=utils.get_today())
        self.btn_date = ctk.CTkButton(form, textvariable=self.selected_date, width=350, height=40, 
                                        fg_color="#333333", hover_color="#444444", text_color="white", border_width=1, border_color="#555555",
                                        command=self.open_calendar, font=ctk.CTkFont(size=14))
        self.btn_date.grid(row=6, column=0, sticky='w', pady=(0,20))
        
        ctk.CTkLabel(form, text="Note (Optional)", font=ctk.CTkFont(weight="bold")).grid(row=7, column=0, sticky='w', pady=(0,5))
        self.ent_note = ctk.CTkEntry(form, width=350, height=40, placeholder_text="What was this for?")
        self.ent_note.grid(row=8, column=0, sticky='w', pady=(0,30))
        
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=9, column=0, sticky='w')
        ctk.CTkButton(btn_frame, text="Add Expense", font=ctk.CTkFont(weight="bold"), height=40, command=self.save_expense).pack(side='left', padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Clear Form", font=ctk.CTkFont(weight="bold"), height=40, fg_color="transparent", border_width=1, command=self.clear_form).pack(side='left')
        
        self.lbl_status = ctk.CTkLabel(form, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_status.grid(row=10, column=0, sticky='w', pady=(20,0))
        
    def _select_tag(self, tag_val):
        self.selected_tag.set(tag_val)
        for val, btn in self.bubble_buttons:
            if val == tag_val:
                btn.configure(fg_color="#3b8ed0")
            else:
                btn.configure(fg_color="#444444")
                
        if tag_val == "Other":
            self.ent_custom_tag.grid(row=4, column=0, sticky='w', pady=(0, 20))
        else:
            self.ent_custom_tag.grid_remove()
            self.ent_custom_tag.delete(0, 'end')

    def open_calendar(self):
        top = ctk.CTkToplevel(self)
        top.title("Select Date")
        top.geometry("350x380")
        top.transient(self.winfo_toplevel())
        top.grab_set()
        try:
            curr_date = datetime.datetime.strptime(self.selected_date.get(), "%Y-%m-%d")
        except:
            curr_date = datetime.datetime.now()

        header_frame = ctk.CTkFrame(top, fg_color="transparent")
        header_frame.pack(fill='x', padx=10, pady=(15, 0))
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        var_month = ctk.StringVar(value=months[curr_date.month - 1])
        var_year = ctk.StringVar(value=str(curr_date.year))
        year_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        year_frame.pack(side='left', padx=(10, 0))

        #SpinBox for Year
        def increase_year():
            var_year.set(str(int(var_year.get()) + 1))
            update_cal()
        def decrease_year():
            var_year.set(str(int(var_year.get()) - 1))
            update_cal()

        btn_minus = ctk.CTkButton(year_frame, text="-", width=35, command=decrease_year)
        btn_minus.pack(side='left')
        lbl_year = ctk.CTkLabel(year_frame, textvariable=var_year, width=70, anchor='center')
        lbl_year.pack(side='left', padx=5)
        btn_plus = ctk.CTkButton(year_frame, text="+", width=35, command=increase_year)
        btn_plus.pack(side='left')
                    
        cal = tkcalendar.Calendar(top, selectmode='day', 
                                  year=curr_date.year, month=curr_date.month, day=curr_date.day,
                                  date_pattern='yyyy-mm-dd',
                                  font="Arial 12",
                                  background="#2b2b2b", selectbackground="#3b8ed0", 
                                  foreground="white", normalbackground="#2b2b2b",
                                  normalforeground="white", headersbackground="#333333",
                                  headersforeground="white", bordercolor="#2b2b2b", borderwidth=0,
                                  weekendbackground="#2b2b2b", weekendforeground="white",
                                  othermonthforeground="#555555", othermonthbackground="#2b2b2b",
                                  othermonthweforeground="#555555", othermonthwebackground="#2b2b2b")
                                  
        # Hide default tkcalendar header to allow custom CTkDropdowns
        if hasattr(cal, '_header'):
            cal._header.pack_forget()
            
        def update_cal(*args):
            m_idx = months.index(var_month.get()) + 1
            y_val = int(var_year.get())
            cal._date = datetime.date(y_val, m_idx, 1)
            cal._display_calendar()

        cb_month = ctk.CTkOptionMenu(header_frame, values=months, variable=var_month, command=update_cal, width=160, fg_color="#333333", button_color="#444444")
        cb_month.pack(side='right', padx=(0, 20))
        cal.pack(fill='both', expand=True, padx=20, pady=20)
        
        def on_date_select(event):
            self.selected_date.set(cal.get_date())
            top.destroy()
            
        cal.bind("<<CalendarSelected>>", on_date_select)

    def on_show(self):
        clear_frame(self.tags_frame)
        self.bubble_buttons = []
        cats = expense.get_all_categories()
        
        for c in cats:
            if c.lower() == 'other':
                continue
            btn = ctk.CTkButton(self.tags_frame, text=utils.get_category_display(c), command=lambda v=c: self._select_tag(v), corner_radius=20, height=32, width=1)
            btn.pack(side='left', padx=(0, 10))
            self.bubble_buttons.append((c, btn))
            
        btn_other = ctk.CTkButton(self.tags_frame, text=utils.get_category_display("Other"), command=lambda: self._select_tag("Other"), corner_radius=20, height=32, width=1)
        btn_other.pack(side='left', padx=(0, 10))
        self.bubble_buttons.append(("Other", btn_other))
        
        self.clear_form()
        
    def clear_form(self):
        self.ent_amount.delete(0, 'end')
        self.selected_date.set(utils.get_today())
        self.ent_note.delete(0, 'end')
        self.lbl_status.configure(text="")
        if self.bubble_buttons:
            self._select_tag(self.bubble_buttons[0][0])
        
    def save_expense(self):
        amt = self.ent_amount.get()
        date = self.selected_date.get()
        note = self.ent_note.get()
        
        cat = self.selected_tag.get()
        if cat == "Other":
            cat = self.ent_custom_tag.get()
            
        v_amt, m_amt = utils.validate_amount(amt)
        if not v_amt:
            self.lbl_status.configure(text=m_amt, text_color=COLOR_DANGER)
            return
            
        v_date, m_date = utils.validate_date(date)
        if not v_date:
            self.lbl_status.configure(text=m_date, text_color=COLOR_DANGER)
            return
            
        if not str(cat).strip():
            self.lbl_status.configure(text="Please provide a category tag.", text_color=COLOR_DANGER)
            return

        success = expense.add_expense(amt, cat, date, note)
        if success:
            show_auto_dismiss_message(self.lbl_status, "Expense saved successfully!", COLOR_SUCCESS)
            self.on_show() # Refresh bubbles to show new tag immediately if custom
        else:
            self.lbl_status.configure(text="Database save failed.", text_color=COLOR_DANGER)

class ViewExpensesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(header, text="Browse Expenses", font=ctk.CTkFont(size=28, weight="bold")).pack(side='left')
        ctk.CTkLabel(header, text="Filter:", font=ctk.CTkFont(weight="bold")).pack(side='left', padx=(40, 10))
        self.var_filter = ctk.StringVar(value="All")
        self.cb = ctk.CTkComboBox(header, variable=self.var_filter, values=["All"], command=self.load_expenses, state='readonly')
        self.cb.pack(side='left')
        
        h_row = ctk.CTkFrame(self, fg_color="transparent")
        h_row.pack(fill='x', padx=20, pady=(0, 5))
        ctk.CTkLabel(h_row, text="Date", font=ctk.CTkFont(weight="bold"), text_color="grey", width=120, anchor='w').pack(side='left')
        ctk.CTkLabel(h_row, text="Category", font=ctk.CTkFont(weight="bold"), text_color="grey", width=110, anchor='center').pack(side='left', padx=10)
        ctk.CTkLabel(h_row, text="Note", font=ctk.CTkFont(weight="bold"), text_color="grey", anchor='w').pack(side='left', fill='x', expand=True, padx=20)
        ctk.CTkLabel(h_row, text="Amount", font=ctk.CTkFont(weight="bold"), text_color="grey", width=150, anchor='e').pack(side='right')
        
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=COLOR_SURFACE, corner_radius=15)
        self.list_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill='x')
        self.lbl_total = ctk.CTkLabel(bottom, text="Total: Rs 0", font=ctk.CTkFont(size=24, weight="bold"), text_color="#3b8ed0")
        self.lbl_total.pack(side='right')
        
    def render_row(self, exp_id, date, category, amount, note):
        row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        row.pack(fill='x', pady=8, padx=10)
        
        ctk.CTkLabel(row, text=date, font=ctk.CTkFont(size=14, weight="bold"), width=120, anchor='w').pack(side='left')
        
        cat_badge = ctk.CTkFrame(row, fg_color="#3b8ed0", corner_radius=10, height=25)
        cat_badge.pack(side='left', padx=10)
        cat_badge.pack_propagate(False)
        ctk.CTkLabel(cat_badge, text=utils.get_category_display(category), font=ctk.CTkFont(size=12, weight="bold"), text_color="white", width=90).pack(expand=True)
        
        ctk.CTkLabel(row, text=note, font=ctk.CTkFont(size=14), text_color="grey", anchor='w').pack(side='left', fill='x', expand=True, padx=20)
        
        btn_del = ctk.CTkButton(row, text="✕", width=30, fg_color="transparent", text_color=COLOR_DANGER, hover_color="#3d1e1e", command=lambda: self.delete_expense(exp_id))
        btn_del.pack(side='right')
        
        btn_edit = ctk.CTkButton(row, text="✎", width=30, fg_color="transparent", text_color="white", hover_color="#444444", command=lambda: self.open_edit_dialog(exp_id, amount, category, date, note))
        btn_edit.pack(side='right')
        
        ctk.CTkLabel(row, text=utils.format_currency(amount), font=ctk.CTkFont(size=16, weight="bold"), width=120, anchor='e').pack(side='right', padx=(0, 10))

    def on_show(self):
        cats = expense.get_all_categories()
        self.cb.configure(values=["All"] + cats)
        self.var_filter.set("All")
        self.load_expenses()
        
    def load_expenses(self, _=None):
        clear_frame(self.list_frame)
        cat = self.var_filter.get()
        expenses = expense.get_all_expenses() if cat == "All" else expense.get_expenses_by_category(cat)
            
        if not expenses:
            ctk.CTkLabel(self.list_frame, text="No records found in this category.", text_color="grey").pack(pady=40)
            self.lbl_total.configure(text="Total: Rs 0")
            return
            
        total = sum(e['amount'] for e in expenses)
        for e in expenses:
            self.render_row(e['id'], e['date'], e['category'], e['amount'], e['note'])
            
        self.lbl_total.configure(text=f"Total: {utils.format_currency(total)}")
        
    def open_edit_dialog(self, exp_id, amount, category, date, note):
        top = ctk.CTkToplevel(self)
        top.title("Edit Expense")
        top.geometry("400x450")
        top.transient(self.winfo_toplevel())
        top.grab_set()
        
        form = ctk.CTkFrame(top, fg_color="transparent")
        form.pack(pady=30, padx=30, fill='both', expand=True)
        form.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(form, text="Amount (Rs)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky='w', pady=(0,5))
        ent_amount = ctk.CTkEntry(form, height=40)
        ent_amount.grid(row=1, column=0, sticky='ew', pady=(0, 15))
        ent_amount.insert(0, str(amount))
        
        ctk.CTkLabel(form, text="Category", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky='w', pady=(0,5))
        cats = expense.get_all_categories()
        cb_category = ctk.CTkComboBox(form, values=cats, height=40)
        cb_category.grid(row=3, column=0, sticky='ew', pady=(0, 15))
        cb_category.set(category)
        
        ctk.CTkLabel(form, text="Date (YYYY-MM-DD)", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, sticky='w', pady=(0,5))
        ent_date = ctk.CTkEntry(form, height=40)
        ent_date.grid(row=5, column=0, sticky='ew', pady=(0, 15))
        ent_date.insert(0, date)
        
        ctk.CTkLabel(form, text="Note", font=ctk.CTkFont(weight="bold")).grid(row=6, column=0, sticky='w', pady=(0,5))
        ent_note = ctk.CTkEntry(form, height=40)
        ent_note.grid(row=7, column=0, sticky='ew', pady=(0, 25))
        ent_note.insert(0, note)
        
        lbl_status = ctk.CTkLabel(form, text="", font=ctk.CTkFont(weight="bold"))
        lbl_status.grid(row=9, column=0, sticky='w')
        
        def save_changes():
            v_amt, m_amt = utils.validate_amount(ent_amount.get())
            if not v_amt:
                lbl_status.configure(text=m_amt, text_color=COLOR_DANGER)
                return
            v_date, m_date = utils.validate_date(ent_date.get())
            if not v_date:
                lbl_status.configure(text=m_date, text_color=COLOR_DANGER)
                return
            
            cat_val = cb_category.get()
            if not str(cat_val).strip():
                lbl_status.configure(text="Category cannot be empty.", text_color=COLOR_DANGER)
                return
                
            success = expense.update_expense(exp_id, ent_amount.get(), cat_val, ent_date.get(), ent_note.get())
            if success:
                top.destroy()
                self.load_expenses()
            else:
                lbl_status.configure(text="Update failed.", text_color=COLOR_DANGER)
                
        ctk.CTkButton(form, text="Save Changes", font=ctk.CTkFont(weight="bold"), height=40, command=save_changes).grid(row=8, column=0, sticky='w')

    def delete_expense(self, exp_id):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete this expense permanently?")
        if confirm:
            if expense.delete_expense(exp_id):
                self.load_expenses()

class MonthlySummaryFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill='x', pady=(0, 20))
        ctk.CTkLabel(header, text="Monthly History", font=ctk.CTkFont(size=28, weight="bold")).pack(side='left')
        
        # Split vertical
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=COLOR_SURFACE, corner_radius=15, height=200)
        self.list_frame.pack(fill='x', expand=False, pady=(0, 20))
        
        self.trend_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=15)
        self.trend_frame.pack(fill='both', expand=True)

    def on_show(self):
        clear_frame(self.list_frame)
        clear_frame(self.trend_frame)
        
        summary = analytics.get_monthly_summary()
        
        if not summary:
            ctk.CTkLabel(self.list_frame, text="No records.", text_color="grey").pack(pady=40)
            return
            
        for row in summary:
            item = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            item.pack(fill='x', pady=12, padx=20)
            ctk.CTkLabel(item, text=utils.format_month(row['month_str']), font=ctk.CTkFont(size=18, weight="bold")).pack(side='left')
            ctk.CTkLabel(item, text=utils.format_currency(row['total']), font=ctk.CTkFont(size=18, weight="bold"), text_color="#3b8ed0").pack(side='right')
            ctk.CTkFrame(self.list_frame, height=1, fg_color="#333333").pack(fill='x', padx=20)
            
        # Draw Trend chart
        fig_trend = analytics.get_monthly_trend_figure()
        if fig_trend:
            canvas = FigureCanvasTkAgg(fig_trend, master=self.trend_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, pady=10, padx=10)

class SetBudgetFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        ctk.CTkLabel(self, text="Budget", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor='w', pady=(0, 20))
        
        card = ctk.CTkFrame(self, fg_color="transparent")
        card.pack(fill='x', pady=(0, 20))
        
        # Section 1: Total Monthly Budget
        monthly_card = ctk.CTkFrame(card, fg_color=COLOR_SURFACE, corner_radius=15)
        monthly_card.pack(fill='x', pady=(0, 15), ipadx=20, ipady=15)
        
        ctk.CTkLabel(monthly_card, text="Monthly Budget", font=ctk.CTkFont(size=18, weight="bold"), text_color="#3b8ed0").grid(row=0, column=0, columnspan=3, sticky='w', padx=20, pady=(5,15))
        
        ctk.CTkLabel(monthly_card, text="Total Monthly Limit (Rs)", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky='w', padx=20, pady=(0,5))
        self.ent_total_limit = ctk.CTkEntry(monthly_card, width=200, height=40, placeholder_text="e.g. 50000")
        self.ent_total_limit.grid(row=2, column=0, sticky='w', padx=20, pady=(0,10))
        
        btn_total_frame = ctk.CTkFrame(monthly_card, fg_color="transparent")
        btn_total_frame.grid(row=2, column=1, sticky='w')
        ctk.CTkButton(btn_total_frame, text="Save Total Limit", height=40, font=ctk.CTkFont(weight="bold"), command=lambda: self.save_budget('GLOBAL_TOTAL', self.ent_total_limit.get())).pack(side='left', padx=(0,10))
        ctk.CTkButton(btn_total_frame, text="Remove", height=40, font=ctk.CTkFont(weight="bold"), fg_color="transparent", border_width=1, command=lambda: self.clear_budget('GLOBAL_TOTAL'), hover_color="#3d1e1e", text_color=COLOR_DANGER).pack(side='left')
        
        # Section 2: Category Budgets
        cat_card = ctk.CTkFrame(card, fg_color=COLOR_SURFACE, corner_radius=15)
        cat_card.pack(fill='x', ipadx=20, ipady=15)
        
        ctk.CTkLabel(cat_card, text="Category Budgets", font=ctk.CTkFont(size=18, weight="bold"), text_color="#3b8ed0").grid(row=0, column=0, columnspan=3, sticky='w', padx=20, pady=(5,15))
        
        ctk.CTkLabel(cat_card, text="Category", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky='w', padx=20, pady=(0,5))
        self.cb_category = ctk.CTkComboBox(cat_card, values=[], width=200, height=40)
        self.cb_category.grid(row=2, column=0, sticky='w', padx=20, pady=(0,10))
        
        ctk.CTkLabel(cat_card, text="Limit per Category (Rs)", font=ctk.CTkFont(weight="bold")).grid(row=1, column=1, sticky='w', padx=20, pady=(0,5))
        self.ent_limit = ctk.CTkEntry(cat_card, width=200, height=40, placeholder_text="0.0")
        self.ent_limit.grid(row=2, column=1, sticky='w', padx=20, pady=(0,10))
        
        btn_cat_frame = ctk.CTkFrame(cat_card, fg_color="transparent")
        btn_cat_frame.grid(row=2, column=2, sticky='w', padx=20)
        ctk.CTkButton(btn_cat_frame, text="Save Category", height=40, font=ctk.CTkFont(weight="bold"), command=lambda: self.save_budget(self.cb_category.get(), self.ent_limit.get())).pack(side='left', padx=(0,10))
        ctk.CTkButton(btn_cat_frame, text="Remove", height=40, font=ctk.CTkFont(weight="bold"), fg_color="transparent", border_width=1, command=lambda: self.clear_budget(self.cb_category.get()), hover_color="#3d1e1e", text_color=COLOR_DANGER).pack(side='left')
        
        self.lbl_status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_status.pack(anchor='w', pady=(0, 10))
        
        ctk.CTkLabel(self, text="Current Health Dashboard", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor='w', pady=(10, 10))
        
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=COLOR_SURFACE, corner_radius=15)
        self.list_frame.pack(fill='both', expand=True, pady=(0, 20))

    def on_show(self):
        cats = expense.get_all_categories()
        cats = [c for c in cats if c != 'GLOBAL_TOTAL' and c.lower() != 'other']
        self.cb_category.configure(values=cats)
        if cats:
            self.cb_category.set(cats[0])
            
        self.ent_limit.delete(0, 'end')
        self.ent_total_limit.delete(0, 'end')
        self.lbl_status.configure(text="")
        self.load_status()
        
    def load_status(self):
        clear_frame(self.list_frame)
        status_data = analytics.get_budget_status()
        if not status_data:
            ctk.CTkLabel(self.list_frame, text="No budgets configured yet. Set one above!", text_color="grey").pack(pady=40)
            return
            
        # Draw the GLOBAL_TOTAL first if it exists
        global_row = next((r for r in status_data if r[0] == 'GLOBAL_TOTAL'), None)
        if global_row:
            self._render_budget_row(global_row, is_global=True)
            
        # Draw a divider if we have both
        if global_row and len(status_data) > 1:
            ctk.CTkFrame(self.list_frame, height=2, fg_color="#444444").pack(fill='x', padx=20, pady=(10,10))
            
        for row in status_data:
            if row[0] != 'GLOBAL_TOTAL':
                self._render_budget_row(row, is_global=False)

    def _render_budget_row(self, row, is_global):
        cat, limit, spent, status = row
        
        if is_global:
            cat_display = "Total Monthly Limit"
        else:
            cat_display = cat
            
        is_over = (status == 'OVER!')
        
        item = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        item.pack(fill='x', pady=10, padx=20)
        
        title_font = ctk.CTkFont(size=20, weight="bold") if is_global else ctk.CTkFont(size=18, weight="bold")
        title_color = "#3b8ed0" if is_global else "white"
        
        ctk.CTkLabel(item, text=utils.get_category_display(cat_display), font=title_font, text_color=title_color, width=200, anchor='w').pack(side='left')
        
        prog_val = min(spent / limit if limit > 0 else 0, 1.0)
        progress = ctk.CTkProgressBar(item, width=350, height=14 if is_global else 12, progress_color=COLOR_DANGER if is_over else COLOR_SUCCESS)
        progress.pack(side='left', padx=20)
        progress.set(prog_val)
        
        status_color = COLOR_DANGER if is_over else COLOR_SUCCESS
        ctk.CTkLabel(item, text=status, font=ctk.CTkFont(size=14, weight="bold"), text_color=status_color).pack(side='right', padx=(10,0))
        ctk.CTkLabel(item, text=f"{utils.format_currency(spent)} / {utils.format_currency(limit)}", font=ctk.CTkFont(size=14), text_color="grey").pack(side='right')

    def save_budget(self, cat, limit_val):
        valid, msg = utils.validate_amount(limit_val)
        if not valid:
            self.lbl_status.configure(text=msg, text_color=COLOR_DANGER)
            return
            
        if not str(cat).strip():
            self.lbl_status.configure(text="Please provide a category tag.", text_color=COLOR_DANGER)
            return
            
        if db.save_budget(cat, float(limit_val)):
            show_auto_dismiss_message(self.lbl_status, "Budget applied successfully!", COLOR_SUCCESS)
            self.load_status()

    def clear_budget(self, cat):
        conn = db.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM budgets WHERE category = ?", (cat,))
            conn.commit()
            show_auto_dismiss_message(self.lbl_status, f"Budget removed.", COLOR_SUCCESS)
            self.load_status()

class ExportCSVFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        ctk.CTkLabel(self, text="Export Workspace", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor='w', pady=(0, 20))
        ctk.CTkLabel(self, text="Take your data anywhere. Export records as CSV for Google Sheets or Excel.", text_color="grey", font=ctk.CTkFont(size=14)).pack(anchor='w', pady=(0, 20))
        
        card = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=15)
        card.pack(fill='x', pady=(0, 20), ipadx=40, ipady=40)
        
        ctk.CTkLabel(card, text="Category Filter", font=ctk.CTkFont(weight="bold")).pack(anchor='w', padx=40, pady=(10,5))
        self.var_cat = ctk.StringVar(value="All")
        self.cb = ctk.CTkComboBox(card, variable=self.var_cat, values=["All"], width=300, height=40, state='readonly')
        self.cb.pack(anchor='w', padx=40, pady=(0, 30))
        
        ctk.CTkButton(card, text="Generate CSV", font=ctk.CTkFont(weight="bold"), height=45, fg_color="#2fa572", hover_color="#26865c", command=self.export_data).pack(anchor='w', padx=40)
        
        self.lbl_status = ctk.CTkLabel(card, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_status.pack(anchor='w', padx=40, pady=10)
        
    def export_data(self):
        cat = self.var_cat.get()
        expenses = expense.get_all_expenses() if cat == "All" else expense.get_expenses_by_category(cat)
            
        if not expenses:
            self.lbl_status.configure(text="No data found to export.", text_color=COLOR_DANGER)
            return
            
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile=f"export_{utils.get_today()}.csv")
        if not path:
            return
            
        data = [(r['id'], r['amount'], r['category'], r['date'], r['note']) for r in expenses]
        if utils.export_to_csv(data, path):
            show_auto_dismiss_message(self.lbl_status, f"Exported beautifully! Saved to: {os.path.basename(path)}", COLOR_SUCCESS, 5000)

    def on_show(self):
        cats = expense.get_all_categories()
        self.cb.configure(values=["All"] + cats)
        self.var_cat.set("All")

# --- Core Application Window ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Expense Tracker")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(900, 600)
        
        db.initialise_db()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar Layer
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLOR_SURFACE)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)
        
        # Brand Logo
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Expense Tracker", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 40))
        
        # Central Content Layer
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        self.nav_buttons = {}
        
        views = [
            ("Dashboard", DashboardFrame),
            ("Add Expense", AddExpenseFrame),
            ("Browse Expenses", ViewExpensesFrame),
                        ("Monthly History", MonthlySummaryFrame),
            ("Budget", SetBudgetFrame),
            ("Export Data", ExportCSVFrame)
        ]
        
        # Build Sidebar and Views
        for index, (name, FrameClass) in enumerate(views):
            frame = FrameClass(self.content)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
            btn = ctk.CTkButton(self.sidebar, text=f"   {name}", anchor='w', height=45, fg_color="transparent", 
                                text_color="lightgrey", font=ctk.CTkFont(size=14, weight="bold"), 
                                hover_color="#363636", command=lambda n=name: self.show_frame(n))
            btn.grid(row=index+1, column=0, sticky="ew", padx=15, pady=2)
            self.nav_buttons[name] = btn
            
        btn_exit = ctk.CTkButton(self.sidebar, text="   Exit App", anchor='w', height=45, fg_color="transparent", 
                                text_color=COLOR_DANGER, font=ctk.CTkFont(size=14, weight="bold"), hover_color="#3d1e1e", 
                                command=self.destroy)
        btn_exit.grid(row=9, column=0, sticky="ew", padx=15, pady=(0, 20))
        
        self.show_frame("Dashboard")
        
    def show_frame(self, target):
        for name, btn in self.nav_buttons.items():
            btn.configure(fg_color="transparent", text_color="lightgrey")
            
        self.nav_buttons[target].configure(fg_color="#3b8ed0", text_color="white")
        
        frame = self.frames[target]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            frame.on_show()

if __name__ == "__main__":
    app = App()
    app.mainloop()
