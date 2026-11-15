"""
High-Performance Local Web Server for AuraLife
Zero external dependencies - built on Python's native http.server.
Author: Shubhi Mathur
"""

import http.server
import socketserver
import json
import os
import urllib.parse
import webbrowser
import threading
import sys

# Guarantee root path is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.database import DatabaseManager
from core.models import Task, Habit, Expense, Note
from core.analytics import AnalyticsEngine
from core.exporter import DataExporter


class AuraLifeHTTPHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, db=None, analytics=None, exporter=None, **kwargs):
        self.db = db
        self.analytics = analytics
        self.exporter = exporter
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        # Mute normal request logs to keep terminal tidy
        pass

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len > 0:
            raw = self.rfile.read(content_len).decode("utf-8")
            return json.loads(raw)
        return {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/data":
            data = {
                "profile": self.db.profile.to_dict(),
                "tasks": [t.to_dict() for t in self.db.tasks],
                "habits": [
                    {
                        **h.to_dict(),
                        "streak": h.calculate_streak(),
                        "checked_today": h.is_logged_today(),
                    }
                    for h in self.db.habits
                ],
                "expenses": [e.to_dict() for e in self.db.expenses],
                "notes": [n.to_dict() for n in self.db.notes],
                "metrics": {
                    "productivity_score": self.analytics.calculate_productivity_score(),
                    "tasks": self.analytics.get_task_metrics(),
                    "habits": self.analytics.get_habit_metrics(),
                    "financial": self.analytics.get_financial_metrics(),
                    "activity_7d": self.analytics.get_last_7_days_activity(),
                },
            }
            self._send_json(data)
            return

        # Serve index.html or dashboard.html
        if path in ["/", "/index.html", "/dashboard.html"]:
            html_path = os.path.join(os.path.dirname(__file__), "index.html")
            if not os.path.exists(html_path):
                html_path = os.path.join(BASE_DIR, "dashboard.html")
            
            if os.path.exists(html_path):
                with open(html_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
                return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        if path == "/api/task/add":
            task = Task(
                title=body.get("title", "New Task"),
                description=body.get("description", ""),
                category=body.get("category", "General"),
                priority=body.get("priority", "Medium"),
                due_date=body.get("due_date", ""),
            )
            self.db.add_task(task)
            self._send_json({"success": True, "task": task.to_dict()})
            return

        elif path == "/api/task/toggle":
            task_id = body.get("id")
            task = self.db.toggle_task(task_id)
            if task:
                self._send_json({"success": True, "task": task.to_dict()})
            else:
                self._send_json({"success": False, "error": "Task not found"}, 404)
            return

        elif path == "/api/task/delete":
            task_id = body.get("id")
            ok = self.db.delete_task(task_id)
            self._send_json({"success": ok})
            return

        elif path == "/api/habit/toggle":
            habit_id = body.get("id")
            res = self.db.toggle_habit_today(habit_id)
            self._send_json({"success": True, "checked_today": res})
            return

        elif path == "/api/habit/add":
            habit = Habit(
                name=body.get("name", "New Habit"),
                category=body.get("category", "Wellness"),
            )
            self.db.add_habit(habit)
            self._send_json({"success": True, "habit": habit.to_dict()})
            return

        elif path == "/api/expense/add":
            exp = Expense(
                title=body.get("title", "Expense"),
                amount=float(body.get("amount", 0)),
                category=body.get("category", "Food"),
                notes=body.get("notes", ""),
            )
            self.db.add_expense(exp)
            self._send_json({"success": True, "expense": exp.to_dict()})
            return

        elif path == "/api/expense/delete":
            exp_id = body.get("id")
            ok = self.db.delete_expense(exp_id)
            self._send_json({"success": ok})
            return

        elif path == "/api/note/add":
            note = Note(
                title=body.get("title", "Quick Note"),
                category=body.get("category", "Ideas"),
                content=body.get("content", ""),
            )
            self.db.add_note(note)
            self._send_json({"success": True, "note": note.to_dict()})
            return

        elif path == "/api/export":
            t_csv = self.exporter.export_tasks_csv()
            e_csv = self.exporter.export_expenses_csv()
            b_json = self.exporter.export_full_json()
            self._send_json({
                "success": True,
                "tasks_csv": os.path.basename(t_csv),
                "expenses_csv": os.path.basename(e_csv),
                "backup_json": os.path.basename(b_json),
            })
            return

        self.send_response(404)
        self.end_headers()


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_web_server(port=5000, open_browser=True):
    db = DatabaseManager()
    analytics = AnalyticsEngine(db)
    exporter = DataExporter(db)

    def handler_factory(*args, **kwargs):
        return AuraLifeHTTPHandler(*args, db=db, analytics=analytics, exporter=exporter, **kwargs)

    # Bind to 0.0.0.0 to listen on all interfaces
    try:
        server = ReusableTCPServer(("0.0.0.0", port), handler_factory)
    except OSError:
        server = ReusableTCPServer(("127.0.0.1", port), handler_factory)

    url = f"http://127.0.0.1:{port}"

    print(f"\n=============================================================")
    print(f"  * AuraLife Live Dashboard: {url}")
    print(f"  * Created for: {db.profile.name}")
    print(f"=============================================================\n")

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down AuraLife server...")
        server.server_close()


if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    start_web_server(port=port)
