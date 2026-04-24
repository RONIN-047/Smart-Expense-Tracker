# views/monthly.py - Monthly spending history and trend chart
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import db
import analytics
import utils
from views.shared import *


class MonthlySummaryFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        # Scrollable at root level - scrollbar at left edge
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill='both', expand=True, padx=0, pady=0)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill='both', expand=True, padx=30, pady=30)

        # Page header
        ctk.CTkLabel(inner, text="Monthly History",
                     font=("Arial", 32, "bold")).pack(anchor='w', pady=(0, 25))

        # ── Hero card (current month) ──────────────────────────────────
        self.hero_frame = ctk.CTkFrame(inner, fg_color="#0066cc", corner_radius=20)
        self.hero_frame.pack(fill='x', pady=(0, 25))

        hero_inner = ctk.CTkFrame(self.hero_frame, fg_color="transparent")
        hero_inner.pack(fill='x', padx=35, pady=28)
        hero_inner.grid_columnconfigure(0, weight=1)
        hero_inner.grid_columnconfigure(1, weight=0)

        # Left side - main amount
        left = ctk.CTkFrame(hero_inner, fg_color="transparent")
        left.grid(row=0, column=0, sticky='w')

        self.hero_label = ctk.CTkLabel(left, text="This Month",
                                       font=("Arial", 15), text_color="#c0d8f0")
        self.hero_label.pack(anchor='w', pady=(0, 6))

        self.hero_amount = ctk.CTkLabel(left, text="Rs 0.00",
                                        font=("Arial", 44, "bold"), text_color="white", height=55)
        self.hero_amount.pack(anchor='w', pady=(0, 6))

        self.hero_sub = ctk.CTkLabel(left, text="",
                                     font=("Arial", 14), text_color="#a0c4e0")
        self.hero_sub.pack(anchor='w')

        # Right side - stats
        right = ctk.CTkFrame(hero_inner, fg_color="transparent")
        right.grid(row=0, column=1, sticky='e', padx=(20, 0))

        self.stat_vs_last = ctk.CTkLabel(right, text="", font=("Arial", 14), text_color="#a0c4e0", anchor='e')
        self.stat_vs_last.pack(anchor='e', pady=(0, 8))
        self.stat_avg = ctk.CTkLabel(right, text="", font=("Arial", 14), text_color="#a0c4e0", anchor='e')
        self.stat_avg.pack(anchor='e', pady=(0, 8))
        self.stat_months = ctk.CTkLabel(right, text="", font=("Arial", 14), text_color="#a0c4e0", anchor='e')
        self.stat_months.pack(anchor='e')

        # ── Bottom: history list (left) + trend chart (right) ─────────
        bottom_row = ctk.CTkFrame(inner, fg_color="transparent")
        bottom_row.pack(fill='both', expand=True)
        bottom_row.grid_columnconfigure(0, weight=1)
        bottom_row.grid_columnconfigure(1, weight=2)
        bottom_row.grid_rowconfigure(0, weight=1)

        # Left: past months list
        list_card = ctk.CTkFrame(bottom_row, fg_color=COLOR_SURFACE, corner_radius=18,
                                 border_width=1, border_color="#333344")
        list_card.grid(row=0, column=0, sticky='nsew', padx=(0, 15))

        list_header = ctk.CTkFrame(list_card, fg_color="transparent")
        list_header.pack(fill='x', padx=25, pady=(20, 5))
        ctk.CTkLabel(list_header, text="Past Months",
                     font=("Arial", 16, "bold"), text_color=COLOR_PRIMARY).pack(anchor='w')

        self.list_frame = ctk.CTkScrollableFrame(list_card, fg_color="transparent", height=300)
        self.list_frame.pack(fill='both', expand=True, padx=5, pady=(0, 10))

        # Right: trend chart
        chart_card = ctk.CTkFrame(bottom_row, fg_color=COLOR_SURFACE, corner_radius=18,
                                  border_width=1, border_color="#333344")
        chart_card.grid(row=0, column=1, sticky='nsew', padx=(15, 0))

        ctk.CTkLabel(chart_card, text="📈 Spending Trend",
                     font=("Arial", 16, "bold"), text_color=COLOR_PRIMARY).pack(anchor='w', padx=25, pady=(20, 5))

        self.trend_frame = ctk.CTkFrame(chart_card, fg_color="transparent")
        self.trend_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

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

        clear_frame(self.list_frame)
        clear_frame(self.trend_frame)

        summary = analytics.get_monthly_summary()

        if not summary:
            self.hero_amount.configure(text="Rs 0.00")
            self.hero_label.configure(text="No data yet")
            self.hero_sub.configure(text="Add expenses to see your monthly history")
            self.stat_vs_last.configure(text="")
            self.stat_avg.configure(text="")
            self.stat_months.configure(text="")
            ctk.CTkLabel(self.list_frame, text="No records yet.",
                         text_color="#666", font=("Arial", 14)).pack(pady=40)
            return

        # Current month data
        now = datetime.datetime.now()
        curr_month_str = now.strftime('%Y-%m')
        curr_month_display = now.strftime('%B %Y')

        current = next((r for r in summary if r['month_str'] == curr_month_str), None)
        curr_total = current['total'] if current else 0.0

        # Past months (exclude current)
        past = [r for r in summary if r['month_str'] != curr_month_str]

        # Stats
        all_totals = [r['total'] for r in summary]
        avg = sum(all_totals) / len(all_totals) if all_totals else 0
        last_total = past[0]['total'] if past else None

        # Update hero card
        self.hero_label.configure(text=f"This Month — {curr_month_display}")
        self.hero_amount.configure(text=utils.format_currency(curr_total))

        if curr_total == max(all_totals) and len(all_totals) > 1:
            self.hero_sub.configure(text="⚠️ Your highest spending month")
        elif curr_total < avg:
            self.hero_sub.configure(text="✓ Below your monthly average")
        else:
            self.hero_sub.configure(text="")

        # Right stats
        if last_total and last_total > 0:
            diff_pct = ((curr_total - last_total) / last_total) * 100
            sign = "+" if diff_pct >= 0 else ""
            color_hint = "↑" if diff_pct >= 0 else "↓"
            self.stat_vs_last.configure(text=f"vs last month: {color_hint} {sign}{diff_pct:.0f}%")
        else:
            self.stat_vs_last.configure(text="vs last month: —")

        self.stat_avg.configure(text=f"monthly avg: {utils.format_currency(avg)}")
        self.stat_months.configure(text=f"months tracked: {len(summary)}")

        # Past months list - include ALL months, highlight current
        max_total = max(r['total'] for r in summary) if summary else 1
        for i, row in enumerate(summary):
            is_current = row['month_str'] == curr_month_str
            item = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            item.pack(fill='x', padx=15, pady=8)

            top = ctk.CTkFrame(item, fg_color="transparent")
            top.pack(fill='x')

            month_text = f"📅 {utils.format_month(row['month_str'])}"
            if is_current:
                month_text = f"⭐ {utils.format_month(row['month_str'])} (Now)"

            ctk.CTkLabel(top, text=month_text,
                         font=("Arial", 15, "bold"),
                         text_color=COLOR_PRIMARY if is_current else "white").pack(side='left')
            ctk.CTkLabel(top, text=utils.format_currency(row['total']),
                         font=("Arial", 15, "bold"), text_color=COLOR_PRIMARY).pack(side='right')

            # Mini bar
            bar_pct = row['total'] / max_total if max_total > 0 else 0
            bar_wrap = ctk.CTkFrame(item, fg_color="#1c2847", corner_radius=6, height=6)
            bar_wrap.pack(fill='x', pady=(5, 0))
            bar_wrap.pack_propagate(False)
            bar_fill = ctk.CTkFrame(bar_wrap, fg_color=COLOR_PRIMARY if is_current else "#4a6080",
                                    corner_radius=6, height=6)
            bar_fill.place(relx=0, rely=0, relwidth=bar_pct, relheight=1)

            if i < len(summary) - 1:
                ctk.CTkFrame(item, height=1, fg_color="#333344").pack(fill='x', pady=(10, 0))

        # Trend chart
        try:
            fig_trend = analytics.get_monthly_trend_figure()
            if fig_trend:
                canvas = FigureCanvasTkAgg(fig_trend, master=self.trend_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        except Exception as e:
            print(f"Error generating trend chart: {e}")
            ctk.CTkLabel(self.trend_frame, text="Chart unavailable",
                         text_color="#666", font=("Arial", 14)).pack(pady=40)
