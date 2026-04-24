# views/add_expense.py - Form view for adding new expenses
import customtkinter as ctk
import tkcalendar
import datetime
import expense
import analytics
import utils
from views.shared import *

# Purple Premium Theme Colors
PURPLE_ACCENT = "#b794f6"
PURPLE_BG = "#2a1a3e"
PURPLE_INPUT_BG = "#1a0a2e"
PURPLE_BORDER = "#4a3a5e"
PURPLE_LABEL = "#c8b8d8"  # Lighter purple for better visibility


class AddExpenseFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Regular container - no scroll needed
        scroll = ctk.CTkFrame(self, fg_color="transparent")
        scroll.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Page Header
        ctk.CTkLabel(scroll, text="Add New Expense", font=("Arial", 32, "bold")).pack(anchor='w', pady=(0, 30))
        
        # Main Layout: Form + Preview side by side
        layout_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        layout_grid.pack(fill='both', expand=True)
        layout_grid.grid_columnconfigure(0, weight=1, minsize=500)  # Form column
        layout_grid.grid_columnconfigure(1, weight=1, minsize=400)  # Preview column - bigger!
        layout_grid.grid_rowconfigure(0, weight=1)
        
        # LEFT SIDE: Form Card
        self.card = ctk.CTkFrame(layout_grid, fg_color=PURPLE_BG, corner_radius=20, border_width=1, border_color=PURPLE_BORDER)
        self.card.grid(row=0, column=0, sticky='nsew', padx=(0, 15))
        
        form = ctk.CTkFrame(self.card, fg_color="transparent")
        form.pack(pady=40, padx=40, anchor='nw', fill='both', expand=True)
        form.grid_columnconfigure(0, weight=1)
        
        # Amount Field
        ctk.CTkLabel(form, text="Amount (Rs)", font=("Arial", 16, "bold"), text_color=PURPLE_ACCENT).grid(row=0, column=0, sticky='w', pady=(0,8))
        self.ent_amount = ctk.CTkEntry(form, height=50, placeholder_text="e.g. 1500", fg_color=PURPLE_INPUT_BG, border_color=PURPLE_BORDER, font=("Arial", 16))
        self.ent_amount.grid(row=1, column=0, sticky='ew', pady=(0,25))
        
        # Category Tags
        ctk.CTkLabel(form, text="Category Tags", font=("Arial", 16, "bold"), text_color=PURPLE_ACCENT).grid(row=2, column=0, sticky='w', pady=(0,8))
        self.tags_frame = ctk.CTkFrame(form, fg_color="transparent")
        self.tags_frame.grid(row=3, column=0, sticky='ew', pady=(0, 10))
        self.selected_tag = ctk.StringVar(value="")
        self.bubble_buttons = []
        self.ent_custom_tag = ctk.CTkEntry(form, height=50, placeholder_text="Type custom tag...", fg_color=PURPLE_INPUT_BG, border_color=PURPLE_BORDER, font=("Arial", 15))
        
        # Date Field
        ctk.CTkLabel(form, text="Date (YYYY-MM-DD)", font=("Arial", 16, "bold"), text_color=PURPLE_ACCENT).grid(row=5, column=0, sticky='w', pady=(0,8))
        self.selected_date = ctk.StringVar(value=utils.get_today())
        self.btn_date = ctk.CTkButton(form, textvariable=self.selected_date, height=50, 
                                        fg_color=PURPLE_INPUT_BG, hover_color="#2a1a3e", text_color="white", border_width=1, border_color=PURPLE_BORDER,
                                        command=self.open_calendar, font=("Arial", 16))
        self.btn_date.grid(row=6, column=0, sticky='ew', pady=(0,25))
        
        # Note Field
        ctk.CTkLabel(form, text="Note (Optional)", font=("Arial", 16, "bold"), text_color=PURPLE_ACCENT).grid(row=7, column=0, sticky='w', pady=(0,8))
        self.ent_note = ctk.CTkEntry(form, height=50, placeholder_text="What was this for?", fg_color=PURPLE_INPUT_BG, border_color=PURPLE_BORDER, font=("Arial", 15))
        self.ent_note.grid(row=8, column=0, sticky='ew', pady=(0,30))
        
        # Buttons
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=9, column=0, sticky='ew')
        ctk.CTkButton(btn_frame, text="Add Expense", font=("Arial", 16, "bold"), height=50, fg_color=PURPLE_ACCENT, text_color="#000000", hover_color="#9a7ad6", command=self.save_expense).pack(side='left', padx=(0, 15), expand=True, fill='x')
        ctk.CTkButton(btn_frame, text="Clear", font=("Arial", 16, "bold"), height=50, fg_color="transparent", border_width=1, border_color=PURPLE_BORDER, hover_color="#2a1a3e", command=self.clear_form).pack(side='left', expand=True, fill='x')
        
        self.lbl_status = ctk.CTkLabel(form, text="", font=("Arial", 14, "bold"))
        self.lbl_status.grid(row=10, column=0, sticky='w', pady=(20,0))
        
        # RIGHT SIDE: Live Preview Card
        self.preview_card = ctk.CTkFrame(layout_grid, fg_color=PURPLE_BG, corner_radius=20, border_width=1, border_color=PURPLE_BORDER)
        self.preview_card.grid(row=0, column=1, sticky='nsew', padx=(15, 0))
        
        preview_content = ctk.CTkFrame(self.preview_card, fg_color="transparent")
        preview_content.pack(pady=30, padx=30, fill='both', expand=True)
        
        # Preview Title
        ctk.CTkLabel(preview_content, text="📋 Preview", font=("Arial", 20, "bold"), text_color=PURPLE_ACCENT, height=30).pack(anchor='w', pady=(0, 25))
        
        # Preview Items - with explicit heights to prevent clipping
        self.preview_amount_label = ctk.CTkLabel(preview_content, text="Amount", font=("Arial", 14), text_color=PURPLE_LABEL, height=20)
        self.preview_amount_label.pack(anchor='w', pady=(0, 5))
        self.preview_amount_value = ctk.CTkLabel(preview_content, text="Rs 0.00", font=("Arial", 18, "bold"), text_color="white", height=30)
        self.preview_amount_value.pack(anchor='w', pady=(0, 20))
        
        self.preview_category_label = ctk.CTkLabel(preview_content, text="Category", font=("Arial", 14), text_color=PURPLE_LABEL, height=20)
        self.preview_category_label.pack(anchor='w', pady=(0, 5))
        self.preview_category_value = ctk.CTkLabel(preview_content, text="—", font=("Arial", 18, "bold"), text_color="white", height=30)
        self.preview_category_value.pack(anchor='w', pady=(0, 20))
        
        self.preview_date_label = ctk.CTkLabel(preview_content, text="Date", font=("Arial", 14), text_color=PURPLE_LABEL, height=20)
        self.preview_date_label.pack(anchor='w', pady=(0, 5))
        self.preview_date_value = ctk.CTkLabel(preview_content, text=utils.get_today(), font=("Arial", 18, "bold"), text_color="white", height=30, wraplength=350)
        self.preview_date_value.pack(anchor='w', pady=(0, 20))
        
        self.preview_note_label = ctk.CTkLabel(preview_content, text="Note", font=("Arial", 14), text_color=PURPLE_LABEL, height=20)
        self.preview_note_label.pack(anchor='w', pady=(0, 5))
        self.preview_note_value = ctk.CTkLabel(preview_content, text="—", font=("Arial", 18, "bold"), text_color="white", height=30, wraplength=350)
        self.preview_note_value.pack(anchor='w', pady=(0, 30))
        
        # Status Box
        self.preview_status = ctk.CTkFrame(preview_content, fg_color="transparent", corner_radius=10, border_width=1, border_color=PURPLE_ACCENT)
        self.preview_status.pack(fill='x', pady=(10, 0))
        ctk.CTkLabel(self.preview_status, text="✓ Ready to save", font=("Arial", 14), text_color=PURPLE_ACCENT).pack(pady=15)
        
        # Bind events for live preview updates
        self.ent_amount.bind('<KeyRelease>', self._update_preview)
        self.ent_note.bind('<KeyRelease>', self._update_preview)
        
    def _select_tag(self, tag_val):
        self.selected_tag.set(tag_val)
        for val, btn in self.bubble_buttons:
            if val == tag_val:
                btn.configure(fg_color=PURPLE_ACCENT, text_color="#000000")
            else:
                btn.configure(fg_color=PURPLE_BORDER, text_color="white")
        if tag_val == "Other":
            self.ent_custom_tag.grid(row=4, column=0, sticky='ew', pady=(0, 25))
        else:
            self.ent_custom_tag.grid_remove()
            self.ent_custom_tag.delete(0, 'end')
        self._update_preview()
    
    def _update_preview(self, event=None):
        """Update live preview as user types"""
        # Update amount
        amt = self.ent_amount.get().strip()
        if amt:
            try:
                formatted = utils.format_currency(float(amt))
                self.preview_amount_value.configure(text=formatted)
            except:
                self.preview_amount_value.configure(text=f"Rs {amt}")
        else:
            self.preview_amount_value.configure(text="Rs 0.00")
        
        # Update category
        cat = self.selected_tag.get()
        if cat == "Other":
            custom = self.ent_custom_tag.get().strip()
            self.preview_category_value.configure(text=custom if custom else "—")
        elif cat:
            self.preview_category_value.configure(text=utils.get_category_display(cat))
        else:
            self.preview_category_value.configure(text="—")
        
        # Update date
        date = self.selected_date.get()
        if date:
            try:
                dt = datetime.datetime.strptime(date, "%Y-%m-%d")
                formatted_date = dt.strftime("%B %d, %Y")
                self.preview_date_value.configure(text=formatted_date)
            except:
                self.preview_date_value.configure(text=date)
        
        # Update note
        note = self.ent_note.get().strip()
        self.preview_note_value.configure(text=note if note else "—")

    def open_calendar(self):
        top = ctk.CTkToplevel(self)
        top.title("Select Date")
        top.geometry("350x380")
        top.transient(self.winfo_toplevel())
        top.grab_set()
        try: curr_date = datetime.datetime.strptime(self.selected_date.get(), "%Y-%m-%d")
        except: curr_date = datetime.datetime.now()
        header_frame = ctk.CTkFrame(top, fg_color="transparent")
        header_frame.pack(fill='x', padx=10, pady=(15, 0))
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        var_month = ctk.StringVar(value=months[curr_date.month - 1])
        var_year = ctk.StringVar(value=str(curr_date.year))
        year_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        year_frame.pack(side='left', padx=(10, 0))
        def increase_year():
            var_year.set(str(int(var_year.get()) + 1)); update_cal()
        def decrease_year():
            var_year.set(str(int(var_year.get()) - 1)); update_cal()
        ctk.CTkButton(year_frame, text="-", width=35, command=decrease_year).pack(side='left')
        ctk.CTkLabel(year_frame, textvariable=var_year, width=70, anchor='center').pack(side='left', padx=5)
        ctk.CTkButton(year_frame, text="+", width=35, command=increase_year).pack(side='left')
        cal = tkcalendar.Calendar(top, selectmode='day', year=curr_date.year, month=curr_date.month, day=curr_date.day,
                                  date_pattern='yyyy-mm-dd', font="Arial 12",
                                  background="#0f0f1a", selectbackground="#00d2ff", foreground="white", normalbackground="#0f0f1a",
                                  normalforeground="white", headersbackground="#16213e", headersforeground="white",
                                  bordercolor="#0f0f1a", borderwidth=0, weekendbackground="#0f0f1a", weekendforeground="white",
                                  othermonthforeground="#555555", othermonthbackground="#0f0f1a",
                                  othermonthweforeground="#555555", othermonthwebackground="#0f0f1a")
        if hasattr(cal, '_header'): cal._header.pack_forget()
        def update_cal(*args):
            cal._date = datetime.date(int(var_year.get()), months.index(var_month.get()) + 1, 1)
            cal._display_calendar()
        ctk.CTkOptionMenu(header_frame, values=months, variable=var_month, command=update_cal, width=160, fg_color="#16213e", button_color="#333344").pack(side='right', padx=(0, 20))
        cal.pack(fill='both', expand=True, padx=20, pady=20)
        def on_date_select(event):
            self.selected_date.set(cal.get_date())
            top.destroy()
            self._update_preview()
        cal.bind("<<CalendarSelected>>", on_date_select)

    def on_show(self):
        clear_frame(self.tags_frame)
        self.bubble_buttons = []
        for c in expense.get_all_categories():
            if c.lower() == 'other': continue
            btn = ctk.CTkButton(self.tags_frame, text=utils.get_category_display(c), command=lambda v=c: self._select_tag(v), corner_radius=20, height=36, width=1, fg_color=PURPLE_BORDER, text_color="white", font=("Arial", 14), anchor='center')
            btn.pack(side='left', padx=(0, 10), pady=5)
            self.bubble_buttons.append((c, btn))
        btn_other = ctk.CTkButton(self.tags_frame, text=utils.get_category_display("Other"), command=lambda: self._select_tag("Other"), corner_radius=20, height=36, width=1, fg_color=PURPLE_BORDER, text_color="white", font=("Arial", 14), anchor='center')
        btn_other.pack(side='left', padx=(0, 10), pady=5)
        self.bubble_buttons.append(("Other", btn_other))
        self.clear_form()
        
    def clear_form(self):
        self.ent_amount.delete(0, 'end')
        self.selected_date.set(utils.get_today())
        self.ent_note.delete(0, 'end')
        self.lbl_status.configure(text="")
        if self.bubble_buttons: self._select_tag(self.bubble_buttons[0][0])
        self._update_preview()
        
    def save_expense(self):
        amt, date, note = self.ent_amount.get(), self.selected_date.get(), self.ent_note.get()
        cat = self.selected_tag.get()
        if cat == "Other": cat = self.ent_custom_tag.get().strip()
        
        v_amt, m_amt = utils.validate_amount(amt)
        if not v_amt: self.lbl_status.configure(text=m_amt, text_color=COLOR_DANGER); return
        
        v_date, m_date = utils.validate_date(date)
        if not v_date: self.lbl_status.configure(text=m_date, text_color=COLOR_DANGER); return
        
        v_cat, m_cat = utils.validate_category(cat)
        if not v_cat: self.lbl_status.configure(text=m_cat, text_color=COLOR_DANGER); return

        if expense.add_expense(amt, cat, date, note):
            analytics.invalidate_chart_cache()
            show_auto_dismiss_message(self.lbl_status, "Expense saved successfully!", PURPLE_ACCENT)
            def flash_bg(color, steps=0):
                if steps == 0: 
                    self.card.configure(border_color=PURPLE_ACCENT, border_width=2)
                    self.preview_card.configure(border_color=PURPLE_ACCENT, border_width=2)
                    self.after(50, lambda: flash_bg(color, 1))
                elif steps < 6: 
                    self.after(50, lambda: flash_bg(color, steps + 1))
                else: 
                    self.card.configure(border_color=PURPLE_BORDER, border_width=1)
                    self.preview_card.configure(border_color=PURPLE_BORDER, border_width=1)
            flash_bg(PURPLE_ACCENT)
            self.on_show()
        else:
            self.lbl_status.configure(text="Database save failed.", text_color=COLOR_DANGER)
