# views/export_csv.py - Export expenses to CSV files
import customtkinter as ctk
from tkinter import filedialog
import os
import expense
import utils
from views.shared import *


class ExportCSVFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill='x', padx=30, pady=(30, 5))
        ctk.CTkLabel(header, text="Export Data",
                     font=("Arial", 32, "bold")).pack(anchor='w')
        ctk.CTkLabel(header, text="Download your expenses as a CSV file — open it in Google Sheets, Excel, or any spreadsheet app.",
                     font=("Arial", 14), text_color="#666").pack(anchor='w', pady=(6, 0))

        # Two column layout - no expand, natural height
        layout = ctk.CTkFrame(self, fg_color="transparent")
        layout.pack(fill='x', padx=30, pady=(25, 30))
        layout.grid_columnconfigure(0, weight=1)
        layout.grid_columnconfigure(1, weight=1)

        # ── LEFT: Settings card ────────────────────────────────────────
        left_card = ctk.CTkFrame(layout, fg_color=COLOR_SURFACE, corner_radius=18,
                                 border_width=1, border_color="#333344")
        left_card.grid(row=0, column=0, sticky='nsew', padx=(0, 15))

        left_inner = ctk.CTkFrame(left_card, fg_color="transparent")
        left_inner.pack(fill='both', expand=True, padx=30, pady=28)

        ctk.CTkLabel(left_inner, text="Export Settings",
                     font=("Arial", 18, "bold"), text_color=COLOR_PRIMARY).pack(anchor='w', pady=(0, 20))

        # Category filter
        ctk.CTkLabel(left_inner, text="Category Filter",
                     font=("Arial", 14, "bold"), text_color="#aaa").pack(anchor='w', pady=(0, 8))
        self.var_cat = ctk.StringVar(value="All")
        self.cb = ctk.CTkComboBox(left_inner, variable=self.var_cat, values=["All"],
                                  height=45, font=("Arial", 14), state='readonly',
                                  fg_color=COLOR_BG, border_color="#333344",
                                  button_color="#333344", button_hover_color="#444455",
                                  command=self._update_preview)
        self.cb.pack(fill='x', pady=(0, 25))

        # Filename
        ctk.CTkLabel(left_inner, text="Filename",
                     font=("Arial", 14, "bold"), text_color="#aaa").pack(anchor='w', pady=(0, 8))
        self.ent_filename = ctk.CTkEntry(left_inner, height=45,
                                         placeholder_text="export_2026-04-21.csv",
                                         fg_color=COLOR_BG, border_color="#333344",
                                         font=("Arial", 14))
        self.ent_filename.pack(fill='x', pady=(0, 30))

        # Export button
        ctk.CTkButton(left_inner, text="📥  Generate & Download",
                      height=50, font=("Arial", 15, "bold"),
                      fg_color=COLOR_SUCCESS, text_color="#000000",
                      hover_color="#00c480",
                      command=self.export_data).pack(fill='x')

        # Status label
        self.lbl_status = ctk.CTkLabel(left_inner, text="",
                                        font=("Arial", 13, "bold"))
        self.lbl_status.pack(anchor='w', pady=(12, 0))

        # ── RIGHT: Live Preview card ───────────────────────────────────
        right_card = ctk.CTkFrame(layout, fg_color=COLOR_SURFACE, corner_radius=18,
                                  border_width=1, border_color="#333344")
        right_card.grid(row=0, column=1, sticky='nsew', padx=(15, 0))

        right_inner = ctk.CTkFrame(right_card, fg_color="transparent")
        right_inner.pack(fill='both', expand=True, padx=30, pady=28)

        ctk.CTkLabel(right_inner, text="Preview",
                     font=("Arial", 18, "bold"), text_color=COLOR_PRIMARY).pack(anchor='w', pady=(0, 20))

        # Preview rows
        preview_rows = ctk.CTkFrame(right_inner, fg_color="transparent")
        preview_rows.pack(fill='x', pady=(0, 20))

        def make_row(parent, label):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill='x', pady=10)
            ctk.CTkLabel(row, text=label, font=("Arial", 14),
                         text_color="#888", anchor='w').pack(side='left')
            val = ctk.CTkLabel(row, text="—", font=("Arial", 14, "bold"),
                               text_color="white", anchor='e')
            val.pack(side='right')
            # Separator
            ctk.CTkFrame(parent, height=1, fg_color="#1c2847").pack(fill='x')
            return val

        self.prev_records  = make_row(preview_rows, "Records to export")
        self.prev_total    = make_row(preview_rows, "Total amount")
        self.prev_range    = make_row(preview_rows, "Date range")
        self.prev_cats     = make_row(preview_rows, "Categories")
        self.prev_filename = make_row(preview_rows, "Filename")

        # Ready status box
        self.ready_box = ctk.CTkFrame(right_inner, fg_color="#0f1a0f",
                                       corner_radius=12, border_width=1,
                                       border_color=COLOR_SUCCESS)
        self.ready_box.pack(fill='x', pady=(10, 0))
        self.ready_label = ctk.CTkLabel(self.ready_box,
                                         text="✓ Ready to export",
                                         font=("Arial", 14, "bold"),
                                         text_color=COLOR_SUCCESS)
        self.ready_label.pack(anchor='w', padx=18, pady=(12, 4))
        self.ready_sub = ctk.CTkLabel(self.ready_box, text="",
                                       font=("Arial", 13), text_color="#666")
        self.ready_sub.pack(anchor='w', padx=18, pady=(0, 12))

    def _update_preview(self, _=None):
        """Refresh the right-side preview panel based on current filter."""
        cat = self.var_cat.get()
        expenses = expense.get_all_expenses() if cat == "All" else expense.get_expenses_by_category(cat)

        count = len(expenses)
        total = sum(e['amount'] for e in expenses)

        if expenses:
            dates = sorted(e['date'] for e in expenses)
            date_min = dates[0]
            date_max = dates[-1]
            if date_min == date_max:
                date_range = date_min
            else:
                date_range = f"{date_min}  →  {date_max}"
            cats_used = len(set(e['category'] for e in expenses))
        else:
            date_range = "—"
            cats_used = 0

        # Filename
        fname = self.ent_filename.get().strip()
        if not fname:
            fname = f"export_{utils.get_today()}.csv"

        self.prev_records.configure(text=str(count))
        self.prev_total.configure(text=utils.format_currency(total),
                                   text_color=COLOR_SUCCESS if count > 0 else "#888")
        self.prev_range.configure(text=date_range)
        self.prev_cats.configure(text=str(cats_used))
        self.prev_filename.configure(text=fname)

        if count > 0:
            self.ready_box.configure(fg_color="#0f1a0f", border_color=COLOR_SUCCESS)
            self.ready_label.configure(text="✓ Ready to export", text_color=COLOR_SUCCESS)
            self.ready_sub.configure(text=f"{count} record{'s' if count != 1 else ''} will be saved")
        else:
            self.ready_box.configure(fg_color="#1a0f0f", border_color=COLOR_DANGER)
            self.ready_label.configure(text="✗ Nothing to export", text_color=COLOR_DANGER)
            self.ready_sub.configure(text="No records match this filter")

    def export_data(self):
        cat = self.var_cat.get()
        expenses = expense.get_all_expenses() if cat == "All" else expense.get_expenses_by_category(cat)
        if not expenses:
            self.lbl_status.configure(text="No data found to export.", text_color=COLOR_DANGER)
            return

        # Use custom filename if provided
        fname = self.ent_filename.get().strip()
        if not fname:
            fname = f"export_{utils.get_today()}.csv"
        if not fname.endswith('.csv'):
            fname += '.csv'

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=fname
        )
        if not path:
            return

        data = [(r['id'], r['amount'], r['category'], r['date'], r['note']) for r in expenses]
        if utils.export_to_csv(data, path):
            show_auto_dismiss_message(
                self.lbl_status,
                f"✓ Saved: {os.path.basename(path)}",
                COLOR_SUCCESS, 5000
            )

    def on_show(self):
        cats = expense.get_all_categories()
        self.cb.configure(values=["All"] + cats)
        self.var_cat.set("All")
        self.ent_filename.delete(0, 'end')
        self.ent_filename.configure(placeholder_text=f"export_{utils.get_today()}.csv")
        self.lbl_status.configure(text="")
        self._update_preview()
