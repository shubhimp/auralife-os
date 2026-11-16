"""
Data Exporter for AuraLife (CSV & JSON)
Author: Shubhi Mathur
"""

import csv
import json
import os
from datetime import datetime
from typing import Optional


class DataExporter:
    """Exports tasks, expenses, and habits into CSV and JSON files."""

    def __init__(self, db, export_dir: Optional[str] = None):
        self.db = db
        if export_dir is None:
            if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
                export_dir = os.path.join("/tmp", "auralife_exports")
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                export_dir = os.path.join(base_dir, "exports")
        self.export_dir = export_dir
        try:
            os.makedirs(self.export_dir, exist_ok=True)
        except OSError:
            self.export_dir = os.path.join("/tmp", "auralife_exports")
            os.makedirs(self.export_dir, exist_ok=True)

    def export_tasks_csv(self) -> str:
        filename = f"auralife_tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.export_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Title", "Category", "Priority", "Due Date", "Completed", "Completed At"])
            for t in self.db.tasks:
                writer.writerow([
                    t.id,
                    t.title,
                    t.category,
                    t.priority,
                    t.due_date,
                    "Yes" if t.completed else "No",
                    t.completed_at or "N/A"
                ])
        return filepath

    def export_expenses_csv(self) -> str:
        filename = f"auralife_expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.export_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Title", "Amount (INR)", "Category", "Date", "Notes"])
            for e in self.db.expenses:
                writer.writerow([
                    e.id,
                    e.title,
                    f"{e.amount:.2f}",
                    e.category,
                    e.date,
                    e.notes
                ])
        return filepath

    def export_full_json(self) -> str:
        filename = f"auralife_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.export_dir, filename)

        data = {
            "exported_at": datetime.now().isoformat(),
            "created_by": "Shubhi Mathur",
            "profile": self.db.profile.to_dict(),
            "tasks": [t.to_dict() for t in self.db.tasks],
            "habits": [h.to_dict() for h in self.db.habits],
            "expenses": [e.to_dict() for e in self.db.expenses],
            "notes": [n.to_dict() for n in self.db.notes]
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        return filepath
