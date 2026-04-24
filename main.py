# main.py - Application entry point and window shell
import sys

# Check for required dependencies before importing
try:
    import customtkinter as ctk
except ImportError:
    print("❌ Error: customtkinter is not installed")
    print("Please install it using: pip install customtkinter")
    print("Or install all dependencies: pip install -r requirements.txt")
    sys.exit(1)

try:
    import matplotlib
except ImportError:
    print("❌ Error: matplotlib is not installed")
    print("Please install it using: pip install matplotlib")
    print("Or install all dependencies: pip install -r requirements.txt")
    sys.exit(1)

try:
    import tkcalendar
except ImportError:
    print("❌ Error: tkcalendar is not installed")
    print("Please install it using: pip install tkcalendar")
    print("Or install all dependencies: pip install -r requirements.txt")
    sys.exit(1)

import db
from views import (
    DashboardFrame, AddExpenseFrame, ViewExpensesFrame,
    MonthlySummaryFrame, SetBudgetFrame, ExportCSVFrame
)
from views.shared import COLOR_BG, COLOR_SIDEBAR, COLOR_PRIMARY, COLOR_DANGER, COLOR_SUCCESS

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 950


class App(ctk.CTk):
    """Core application window with sidebar navigation."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Expense Tracker")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(1100, 700)
        self.configure(fg_color=COLOR_BG)
        
        db.initialise_db()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- Sidebar with Grouped Sections (Option 4 design) ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        # --- Content Area (create BEFORE frames) ---
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        
        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=15, pady=(30, 20), sticky='w')
        ctk.CTkLabel(logo_frame, text="⚡ ", font=("Arial", 22, "bold")).pack(side='left')
        ctk.CTkLabel(logo_frame, text="Expense", font=("Arial", 22, "bold"), text_color=COLOR_SUCCESS).pack(side='left')
        
        self.frames = {}
        self.nav_buttons = {}
        
        # Define sections with views
        sections = [
            ("MAIN", [
                ("Dashboard", DashboardFrame, "🏠"),
                ("Add Expense", AddExpenseFrame, "➕"),
                ("Browse Expenses", ViewExpensesFrame, "📋"),
            ]),
            ("ANALYTICS", [
                ("Monthly History", MonthlySummaryFrame, "📊"),
                ("Budget", SetBudgetFrame, "💰"),
            ]),
            ("TOOLS", [
                ("Export Data", ExportCSVFrame, "📤"),
            ]),
        ]
        
        row_index = 1
        for section_name, views in sections:
            # Section label
            section_label = ctk.CTkLabel(
                self.sidebar, text=section_name,
                font=("Arial", 11, "bold"),
                text_color="#555", anchor='w'
            )
            section_label.grid(row=row_index, column=0, sticky="w", padx=15, pady=(15, 10))
            row_index += 1

            for name, FrameClass, icon in views:
                frame = FrameClass(self.content)
                self.frames[name] = frame
                frame.grid(row=0, column=0, sticky="nsew")

                btn = ctk.CTkButton(
                    self.sidebar, text=f"  {icon}  {name}", anchor='w', height=40,
                    fg_color="transparent", text_color="#888",
                    font=("Arial", 14, "bold"),
                    hover_color="#1c1c2e",
                    border_width=0, border_spacing=0,
                    command=lambda n=name: self.show_frame(n)
                )
                btn.grid(row=row_index, column=0, sticky="ew", padx=10, pady=2)
                self.nav_buttons[name] = btn
                row_index += 1

        # Exit button at bottom
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#1c1c2e").grid(row=row_index, column=0, sticky="ew", padx=15, pady=20)
        ctk.CTkButton(
            self.sidebar, text="  🚪  Exit App", anchor='w', height=40,
            fg_color="transparent", text_color=COLOR_DANGER,
            font=("Arial", 14, "bold"),
            hover_color="#2a1515", command=self.destroy
        ).grid(row=row_index + 1, column=0, sticky="ew", padx=10, pady=(0, 20))
        
        self.show_frame("Dashboard")
        
    def show_frame(self, target):
        """Switch to the given view - populate before raising to avoid flash."""
        for name, btn in self.nav_buttons.items():
            if name == target:
                btn.configure(fg_color="#16213e", text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="#888")
        
        frame = self.frames[target]
        # Populate BEFORE raising - no ghost content flash
        if hasattr(frame, 'on_show'):
            frame.on_show()
        frame.tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()
