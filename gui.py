"""
Desktop GUI Interface for AuraLife
Features dark modern styling, interactive canvas widgets, and graceful fallback.
Author: Shubhi Mathur
"""

import sys
import os

# Guarantee root path is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False


def launch_desktop_gui():
    if not TK_AVAILABLE:
        print("[AuraLife GUI] Tkinter runtime library is not bundled with this Python build.")
        print("[AuraLife GUI] Switching automatically to AuraLife Modern Web Cockpit...")
        from web.server import start_web_server
        start_web_server(port=5000, open_browser=True)
        return

    from core.database import DatabaseManager
    from core.analytics import AnalyticsEngine
    from core.exporter import DataExporter

    db = DatabaseManager()
    analytics = AnalyticsEngine(db)
    exporter = DataExporter(db)

    root = tk.Tk()
    root.title(f"AuraLife — {db.profile.name}'s Command Center")
    root.geometry("980x680")
    root.configure(bg="#0f172a")

    # Header frame
    header = tk.Frame(root, bg="#1e293b", height=65)
    header.pack(fill=tk.X, side=tk.TOP)

    logo_lbl = tk.Label(
        header, text="AL", font=("Segoe UI", 16, "bold"),
        fg="#ffffff", bg="#6366f1", width=3, height=1
    )
    logo_lbl.pack(side=tk.LEFT, padx=(20, 10), pady=12)

    title_frame = tk.Frame(header, bg="#1e293b")
    title_frame.pack(side=tk.LEFT, fill=tk.Y, pady=10)

    title_lbl = tk.Label(
        title_frame, text="AuraLife Command Center",
        font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#1e293b"
    )
    title_lbl.pack(anchor="w")

    subtitle_lbl = tk.Label(
        title_frame, text=f"Crafted with Passion by {db.profile.name}",
        font=("Segoe UI", 9), fg="#38bdf8", bg="#1e293b"
    )
    subtitle_lbl.pack(anchor="w")

    score_val = analytics.calculate_productivity_score()
    score_lbl = tk.Label(
        header, text=f"⚡ Score: {score_val}/100",
        font=("Segoe UI", 11, "bold"), fg="#10b981", bg="#0f172a",
        padx=12, pady=6
    )
    score_lbl.pack(side=tk.RIGHT, padx=20, pady=12)

    # Main notebook/tabs
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TNotebook", background="#0f172a", borderwidth=0)
    style.configure("TNotebook.Tab", background="#1e293b", foreground="#94a3b8", padding=[14, 8], font=("Segoe UI", 10, "bold"))
    style.map("TNotebook.Tab", background=[("selected", "#6366f1")], foreground=[("selected", "#ffffff")])

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

    # Tab 1: Dashboard
    dash_tab = tk.Frame(notebook, bg="#0f172a")
    notebook.add(dash_tab, text=" 📊 Overview ")

    # KPI Row
    kpi_frame = tk.Frame(dash_tab, bg="#0f172a")
    kpi_frame.pack(fill=tk.X, pady=(10, 15))

    t_met = analytics.get_task_metrics()
    h_met = analytics.get_habit_metrics()
    f_met = analytics.get_financial_metrics()

    cards = [
        ("TASKS DONE", f"{t_met['completed']}/{t_met['total']}", f"{t_met['completion_rate']}% rate", "#6366f1"),
        ("HABITS TODAY", f"{h_met['checked_today']}/{h_met['total']}", f"{h_met['best_streak']}d streak", "#10b981"),
        ("BUDGET LEFT", f"₹{f_met['remaining_budget']:,.0f}", f"₹{f_met['total_spent']:,.0f} spent", "#f59e0b"),
    ]

    for title, val, sub, color in cards:
        card = tk.Frame(kpi_frame, bg="#1e293b", padx=16, pady=14, relief=tk.FLAT)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)
        tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg="#94a3b8", bg="#1e293b").pack(anchor="w")
        tk.Label(card, text=val, font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#1e293b").pack(anchor="w", pady=4)
        tk.Label(card, text=sub, font=("Segoe UI", 9), fg=color, bg="#1e293b").pack(anchor="w")

    # Tasks Tab
    tasks_tab = tk.Frame(notebook, bg="#0f172a")
    notebook.add(tasks_tab, text=" 📋 Tasks ")

    task_listbox = tk.Listbox(
        tasks_tab, bg="#1e293b", fg="#ffffff", font=("Segoe UI", 10),
        selectbackground="#6366f1", selectforeground="#ffffff", borderwidth=0, highlightthickness=0
    )
    task_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for t in db.tasks:
        status = "✔" if t.completed else "○"
        task_listbox.insert(tk.END, f" {status} [{t.priority}] {t.title} ({t.category})")

    # Habits Tab
    habits_tab = tk.Frame(notebook, bg="#0f172a")
    notebook.add(habits_tab, text=" ⚡ Habits ")

    for h in db.habits:
        h_row = tk.Frame(habits_tab, bg="#1e293b", padx=12, pady=10)
        h_row.pack(fill=tk.X, padx=10, pady=5)
        st = "✔ Checked" if h.is_logged_today() else "○ Pending"
        tk.Label(h_row, text=h.name, font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#1e293b").pack(side=tk.LEFT)
        tk.Label(h_row, text=f"🔥 {h.calculate_streak()} Days", font=("Segoe UI", 10), fg="#fbbf24", bg="#1e293b").pack(side=tk.LEFT, padx=20)
        tk.Label(h_row, text=st, font=("Segoe UI", 10), fg="#10b981" if h.is_logged_today() else "#94a3b8", bg="#1e293b").pack(side=tk.RIGHT)

    root.mainloop()


if __name__ == "__main__":
    launch_desktop_gui()
