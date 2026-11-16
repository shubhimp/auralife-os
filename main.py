"""
AuraLife - The All-In-One Personal Command Center
Author: Shubhi Mathur
Year: 2026

Entry point for launching AuraLife across Web, Vercel Serverless, GUI, and CLI interfaces.
Exports top-level 'app', 'application', and 'handler' variables for Vercel/WSGI compatibility.
"""

import sys
import os
import json
import urllib.parse

# Guarantee UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Guarantee root path is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.database import DatabaseManager
from core.models import Task, Habit, Expense, Note
from core.analytics import AnalyticsEngine
from core.exporter import DataExporter


# =====================================================================
# Vercel / WSGI Cloud Application Engine
# =====================================================================
def create_wsgi_app():
    """Creates a standard WSGI callable for Vercel, AWS Lambda, or Gunicorn."""
    db = DatabaseManager()
    analytics = AnalyticsEngine(db)
    exporter = DataExporter(db)

    def wsgi_app(environ, start_response):
        path = environ.get("PATH_INFO", "/") or "/"
        method = environ.get("REQUEST_METHOD", "GET").upper()

        # Handle CORS Preflight
        if method == "OPTIONS":
            headers = [
                ("Content-Type", "text/plain"),
                ("Access-Control-Allow-Origin", "*"),
                ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
                ("Access-Control-Allow-Headers", "Content-Type"),
            ]
            start_response("200 OK", headers)
            return [b""]

        # Normalize API route regardless of whether Vercel stripped /api prefix
        api_path = path if path.startswith("/api") else f"/api{path}"

        # GET Requests
        if method == "GET":
            # Serve Cyber White & Yellow UI
            if path in ["/", "/index.html", "/dashboard.html"]:
                html_path = os.path.join(BASE_DIR, "index.html")
                if not os.path.exists(html_path):
                    html_path = os.path.join(BASE_DIR, "web", "index.html")
                if not os.path.exists(html_path):
                    html_path = os.path.join(BASE_DIR, "dashboard.html")

                if os.path.exists(html_path):
                    with open(html_path, "rb") as f:
                        content = f.read()
                    headers = [
                        ("Content-Type", "text/html; charset=utf-8"),
                        ("Content-Length", str(len(content))),
                        ("Access-Control-Allow-Origin", "*"),
                    ]
                    start_response("200 OK", headers)
                    return [content]

            # Serve JSON State Data & Analytics
            elif api_path == "/api/data":
                data = {
                    "profile": db.profile.to_dict(),
                    "tasks": [t.to_dict() for t in db.tasks],
                    "habits": [
                        {
                            **h.to_dict(),
                            "streak": h.calculate_streak(),
                            "checked_today": h.is_logged_today(),
                        }
                        for h in db.habits
                    ],
                    "expenses": [e.to_dict() for e in db.expenses],
                    "notes": [n.to_dict() for n in db.notes],
                    "metrics": {
                        "productivity_score": analytics.calculate_productivity_score(),
                        "tasks": analytics.get_task_metrics(),
                        "habits": analytics.get_habit_metrics(),
                        "financial": analytics.get_financial_metrics(),
                        "activity_7d": analytics.get_last_7_days_activity(),
                    },
                }
                body = json.dumps(data, ensure_ascii=False).encode("utf-8")
                headers = [
                    ("Content-Type", "application/json; charset=utf-8"),
                    ("Content-Length", str(len(body))),
                    ("Access-Control-Allow-Origin", "*"),
                ]
                start_response("200 OK", headers)
                return [body]

        # POST Requests
        elif method == "POST":
            try:
                content_len = int(environ.get("CONTENT_LENGTH", 0) or 0)
            except (ValueError, TypeError):
                content_len = 0

            payload = {}
            if content_len > 0 and "wsgi.input" in environ:
                raw_body = environ["wsgi.input"].read(content_len)
                if raw_body:
                    try:
                        payload = json.loads(raw_body.decode("utf-8"))
                    except Exception:
                        payload = {}

            if api_path == "/api/task/add":
                task = Task(
                    title=payload.get("title", "New Task"),
                    description=payload.get("description", ""),
                    category=payload.get("category", "General"),
                    priority=payload.get("priority", "Medium"),
                    due_date=payload.get("due_date", ""),
                )
                db.add_task(task)
                resp = {"success": True, "task": task.to_dict()}

            elif api_path == "/api/task/toggle":
                task = db.toggle_task(payload.get("id"))
                resp = {"success": True, "task": task.to_dict()} if task else {"success": False, "error": "Not found"}

            elif api_path == "/api/task/delete":
                ok = db.delete_task(payload.get("id"))
                resp = {"success": ok}

            elif api_path == "/api/habit/toggle":
                res = db.toggle_habit_today(payload.get("id"))
                resp = {"success": True, "checked_today": res}

            elif api_path == "/api/habit/add":
                habit = Habit(
                    name=payload.get("name", "New Habit"),
                    category=payload.get("category", "Wellness"),
                )
                db.add_habit(habit)
                resp = {"success": True, "habit": habit.to_dict()}

            elif api_path == "/api/expense/add":
                exp = Expense(
                    title=payload.get("title", "Expense"),
                    amount=float(payload.get("amount", 0)),
                    category=payload.get("category", "Food"),
                    notes=payload.get("notes", ""),
                )
                db.add_expense(exp)
                resp = {"success": True, "expense": exp.to_dict()}

            elif api_path == "/api/expense/delete":
                ok = db.delete_expense(payload.get("id"))
                resp = {"success": ok}

            elif api_path == "/api/note/add":
                note = Note(
                    title=payload.get("title", "Quick Note"),
                    category=payload.get("category", "Ideas"),
                    content=payload.get("content", ""),
                )
                db.add_note(note)
                resp = {"success": True, "note": note.to_dict()}

            elif api_path == "/api/export":
                t_csv = exporter.export_tasks_csv()
                e_csv = exporter.export_expenses_csv()
                b_json = exporter.export_full_json()
                resp = {
                    "success": True,
                    "tasks_csv": os.path.basename(t_csv),
                    "expenses_csv": os.path.basename(e_csv),
                    "backup_json": os.path.basename(b_json),
                }

            else:
                body = json.dumps({"error": "Endpoint not found"}).encode("utf-8")
                start_response("404 Not Found", [("Content-Type", "application/json"), ("Access-Control-Allow-Origin", "*")])
                return [body]

            body = json.dumps(resp, ensure_ascii=False).encode("utf-8")
            headers = [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(body))),
                ("Access-Control-Allow-Origin", "*"),
            ]
            start_response("200 OK", headers)
            return [body]

        # 404 Fallback
        body = b"Not Found"
        start_response("404 Not Found", [("Content-Type", "text/plain"), ("Access-Control-Allow-Origin", "*")])
        return [body]

    return wsgi_app


# Top-level exports for Vercel Serverless Function detection
app = create_wsgi_app()
application = app
handler = app


# =====================================================================
# Local CLI, GUI, and Diagnostic Launcher
# =====================================================================
def print_welcome_banner():
    print("\n" + "=" * 65)
    print("   * AuraLife Personal Productivity & Command Center *")
    print("   * Created with Passion by: Shubhi Mathur")
    print("   * Version: 1.0.0 | Pure Python Architecture")
    print("=" * 65 + "\n")


def run_tests():
    import unittest
    print("[AuraLife Test Runner] Discovering and executing unit tests...")
    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


def export_now():
    db = DatabaseManager()
    exporter = DataExporter(db)
    print("[AuraLife Exporter] Generating data exports...")
    t = exporter.export_tasks_csv()
    e = exporter.export_expenses_csv()
    b = exporter.export_full_json()
    print(f" ✓ Tasks CSV: {t}")
    print(f" ✓ Expenses CSV: {e}")
    print(f" ✓ Backup JSON: {b}")
    print("\nAll files successfully exported to 'exports/' folder.")


def main():
    print_welcome_banner()

    args = sys.argv[1:]

    if "--test" in args or "-t" in args:
        run_tests()
        return

    if "--export" in args:
        export_now()
        return

    if "--cli" in args or "-c" in args:
        from cli import AuraLifeCLI
        cli = AuraLifeCLI()
        cli.main_loop()
        return

    # Default mode: Launch modern interactive GUI dashboard
    print("🚀 Initializing AuraLife Modern Interactive Cockpit...")
    print("💡 Tip: You can also run 'python main.py --cli' for the terminal interface.")
    print("💡 Tip: You can run 'python main.py --test' to run the test suite.\n")

    # Start local web cockpit
    from web.server import start_web_server
    start_web_server(port=5000, open_browser=True)


if __name__ == "__main__":
    main()
