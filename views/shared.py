# views/shared.py - Shared constants, colors, and helper functions used across all views
import customtkinter as ctk

# --- Premium Dark Navy Theme Colors ---
COLOR_SUCCESS = '#00f5a0'
COLOR_WARNING = '#ffd700'
COLOR_DANGER = '#ff6b6b'
COLOR_SURFACE = '#16213e'
COLOR_BG = '#0f0f1a'
COLOR_SIDEBAR = '#0a0a1a'
COLOR_PRIMARY = '#00d2ff'

def clear_frame(frame):
    """Destroy all child widgets inside a frame."""
    for widget in frame.winfo_children():
        widget.destroy()

def show_auto_dismiss_message(label, text, color, delay=3000):
    """Display a temporary status message that auto-dismisses after a delay."""
    label.configure(text=text, text_color=color)
    if hasattr(label, '_timer') and label._timer:
        label.after_cancel(label._timer)
    label._timer = label.after(delay, lambda: label.configure(text=""))
