# views/budget.py - Budget configuration and health dashboard
import customtkinter as ctk
import db
import expense
import analytics
import utils
from views.shared import *


class SetBudgetFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        # Scrollable - AT ROOT LEVEL, no padx so scrollbar is at edge
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill='both', expand=True, padx=0, pady=0)

        # All content inside with padding
        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill='both', expand=True, padx=30, pady=30)

        # ── Page Header ────────────────────────────────────────────────
        ctk.CTkLabel(inner, text="Budget", font=("Arial", 32, "bold")).pack(anchor='w', pady=(0, 25))

        # ── Two cards side by side ─────────────────────────────────────
        cards_row = ctk.CTkFrame(inner, fg_color="transparent")
        cards_row.pack(fill='x', pady=(0, 25))
        cards_row.grid_columnconfigure(0, weight=1)
        cards_row.grid_columnconfigure(1, weight=1)

        # LEFT: Total Monthly Budget card
        left_card = ctk.CTkFrame(cards_row, fg_color=COLOR_SURFACE, corner_radius=18,
                                 border_width=1, border_color="#333344")
        left_card.grid(row=0, column=0, sticky='nsew', padx=(0, 12))

        left_inner = ctk.CTkFrame(left_card, fg_color="transparent")
        left_inner.pack(fill='both', expand=True, padx=30, pady=28)

        ctk.CTkLabel(left_inner, text="Total Monthly Budget",
                     font=("Arial", 18, "bold"), text_color=COLOR_PRIMARY).pack(anchor='w', pady=(0, 5))
        ctk.CTkLabel(left_inner, text="Set a cap for all spending this month.",
                     font=("Arial", 13), text_color="#666").pack(anchor='w', pady=(0, 20))

        ctk.CTkLabel(left_inner, text="Monthly Limit (Rs)",
                     font=("Arial", 14, "bold"), text_color="#aaa").pack(anchor='w', pady=(0, 8))
        self.ent_total_limit = ctk.CTkEntry(left_inner, height=45,
                                            placeholder_text="e.g. 50000",
                                            fg_color=COLOR_BG, border_color="#333344",
                                            font=("Arial", 15))
        self.ent_total_limit.pack(fill='x', pady=(0, 18))

        btn_row_left = ctk.CTkFrame(left_inner, fg_color="transparent")
        btn_row_left.pack(fill='x')
        ctk.CTkButton(btn_row_left, text="Save Limit", height=45,
                      font=("Arial", 14, "bold"), fg_color=COLOR_SUCCESS,
                      text_color="#000000", hover_color="#00c480",
                      command=lambda: self.save_budget('GLOBAL_TOTAL', self.ent_total_limit.get())
                      ).pack(side='left', expand=True, fill='x', padx=(0, 10))
        ctk.CTkButton(btn_row_left, text="Remove", height=45,
                      font=("Arial", 14, "bold"), fg_color="transparent",
                      border_width=1, border_color="#333344",
                      hover_color="#3d1e1e", text_color=COLOR_DANGER,
                      command=lambda: self.clear_budget('GLOBAL_TOTAL')
                      ).pack(side='left', expand=True, fill='x')

        # RIGHT: Category Budget card
        right_card = ctk.CTkFrame(cards_row, fg_color=COLOR_SURFACE, corner_radius=18,
                                  border_width=1, border_color="#333344")
        right_card.grid(row=0, column=1, sticky='nsew', padx=(12, 0))

        right_inner = ctk.CTkFrame(right_card, fg_color="transparent")
        right_inner.pack(fill='both', expand=True, padx=30, pady=28)

        ctk.CTkLabel(right_inner, text="Category Budget",
                     font=("Arial", 18, "bold"), text_color=COLOR_PRIMARY).pack(anchor='w', pady=(0, 5))
        ctk.CTkLabel(right_inner, text="Set a spending limit for a specific category.",
                     font=("Arial", 13), text_color="#666").pack(anchor='w', pady=(0, 20))

        ctk.CTkLabel(right_inner, text="Category",
                     font=("Arial", 14, "bold"), text_color="#aaa").pack(anchor='w', pady=(0, 8))
        self.cb_category = ctk.CTkComboBox(right_inner, values=[], height=45,
                                           font=("Arial", 14), fg_color=COLOR_BG,
                                           border_color="#333344",
                                           button_color="#333344", button_hover_color="#444455")
        self.cb_category.pack(fill='x', pady=(0, 15))

        ctk.CTkLabel(right_inner, text="Limit (Rs)",
                     font=("Arial", 14, "bold"), text_color="#aaa").pack(anchor='w', pady=(0, 8))
        self.ent_limit = ctk.CTkEntry(right_inner, height=45,
                                      placeholder_text="e.g. 10000",
                                      fg_color=COLOR_BG, border_color="#333344",
                                      font=("Arial", 15))
        self.ent_limit.pack(fill='x', pady=(0, 18))

        btn_row_right = ctk.CTkFrame(right_inner, fg_color="transparent")
        btn_row_right.pack(fill='x')
        ctk.CTkButton(btn_row_right, text="Save Category", height=45,
                      font=("Arial", 14, "bold"), fg_color=COLOR_SUCCESS,
                      text_color="#000000", hover_color="#00c480",
                      command=lambda: self.save_budget(self.cb_category.get(), self.ent_limit.get())
                      ).pack(side='left', expand=True, fill='x', padx=(0, 10))
        ctk.CTkButton(btn_row_right, text="Remove", height=45,
                      font=("Arial", 14, "bold"), fg_color="transparent",
                      border_width=1, border_color="#333344",
                      hover_color="#3d1e1e", text_color=COLOR_DANGER,
                      command=lambda: self.clear_budget(self.cb_category.get())
                      ).pack(side='left', expand=True, fill='x')

        # ── Status label ───────────────────────────────────────────────
        self.lbl_status = ctk.CTkLabel(inner, text="", font=("Arial", 14, "bold"))
        self.lbl_status.pack(anchor='w', pady=(0, 8))

        # ── Health Dashboard ───────────────────────────────────────────
        ctk.CTkLabel(inner, text="Health Dashboard",
                     font=("Arial", 22, "bold")).pack(anchor='w', pady=(5, 15))

        self.list_frame = ctk.CTkFrame(inner, fg_color=COLOR_SURFACE, corner_radius=18,
                                       border_width=1, border_color="#333344")
        self.list_frame.pack(fill='both', expand=True)

    def on_show(self):
        cats = [c for c in expense.get_all_categories() if c != 'GLOBAL_TOTAL' and c.lower() != 'other']
        self.cb_category.configure(values=cats)
        if cats: self.cb_category.set(cats[0])
        self.ent_limit.delete(0, 'end')
        self.ent_total_limit.delete(0, 'end')
        self.lbl_status.configure(text="")
        self.load_status()

    def load_status(self):
        clear_frame(self.list_frame)
        status_data = analytics.get_budget_status()
        if not status_data:
            ctk.CTkLabel(self.list_frame, text="No budgets configured yet. Set one above!",
                         text_color="#666", font=("Arial", 15)).pack(pady=50)
            return

        global_row = next((r for r in status_data if r[0] == 'GLOBAL_TOTAL'), None)
        if global_row:
            self._render_budget_row(global_row, is_global=True)

        if global_row and len(status_data) > 1:
            ctk.CTkFrame(self.list_frame, height=1, fg_color="#333344").pack(fill='x', padx=25, pady=5)

        for row in status_data:
            if row[0] != 'GLOBAL_TOTAL':
                self._render_budget_row(row, is_global=False)

    def _render_budget_row(self, row, is_global):
        cat, limit, spent, status = row
        cat_display = "Total Monthly Limit" if is_global else cat
        is_over = (status == 'OVER!')

        item = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        item.pack(fill='x', padx=25, pady=14)
        item.grid_columnconfigure(1, weight=1)

        # Category name
        title_font = ("Arial", 17, "bold") if is_global else ("Arial", 15, "bold")
        title_color = COLOR_PRIMARY if is_global else "white"
        ctk.CTkLabel(item, text=utils.get_category_display(cat_display),
                     font=title_font, text_color=title_color,
                     width=210, anchor='w').grid(row=0, column=0, sticky='w', padx=(0, 20))

        # Progress bar
        prog_val = min(spent / limit if limit > 0 else 0, 1.0)
        if is_over:            bar_color = COLOR_DANGER
        elif prog_val > 0.85:  bar_color = COLOR_WARNING
        else:                  bar_color = COLOR_SUCCESS

        bar_h = 16 if is_global else 12
        progress = ctk.CTkProgressBar(item, height=bar_h, progress_color=bar_color,
                                      corner_radius=bar_h // 2)
        progress.grid(row=0, column=1, sticky='ew', padx=(0, 20))
        progress.set(prog_val)

        # Amounts
        ctk.CTkLabel(item,
                     text=f"{utils.format_currency(spent)} / {utils.format_currency(limit)}",
                     font=("Arial", 13), text_color="#888").grid(row=0, column=2, sticky='e', padx=(0, 15))

        # Status badge
        status_color = COLOR_DANGER if is_over else (COLOR_WARNING if prog_val > 0.85 else COLOR_SUCCESS)
        ctk.CTkLabel(item, text=status, font=("Arial", 13, "bold"),
                     text_color=status_color, width=55, anchor='e').grid(row=0, column=3, sticky='e')

    def _refresh_dashboard(self):
        """Tell the dashboard to re-render immediately."""
        try:
            app = self.winfo_toplevel()
            dashboard = app.frames.get("Dashboard")
            if dashboard:
                dashboard.force_refresh()
                dashboard.on_show()
        except Exception as e:
            print(f"Could not refresh dashboard: {e}")

    def save_budget(self, cat, limit_val):
        valid, msg = utils.validate_amount(limit_val)
        if not valid:
            self.lbl_status.configure(text=msg, text_color=COLOR_DANGER)
            return
        if cat != 'GLOBAL_TOTAL':
            v_cat, m_cat = utils.validate_category(cat)
            if not v_cat:
                self.lbl_status.configure(text=m_cat, text_color=COLOR_DANGER)
                return
        if db.save_budget(cat, float(limit_val)):
            show_auto_dismiss_message(self.lbl_status, "Budget saved!", COLOR_SUCCESS)
            self.load_status()
            self._refresh_dashboard()

    def clear_budget(self, cat):
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM budgets WHERE category = ?", (cat,))
                conn.commit()
            show_auto_dismiss_message(self.lbl_status, "Budget removed.", COLOR_SUCCESS)
            self.load_status()
            self._refresh_dashboard()
        except Exception as e:
            print(f"Error removing budget: {e}")
