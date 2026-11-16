"""
Data persistence and repository manager for AuraLife.
Author: Shubhi Mathur
"""

import json
import os
import shutil
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from core.models import Task, Habit, Expense, Note, UserProfile


class DatabaseManager:
    """Handles JSON-backed persistent data with automatic backup and seed initializers."""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            # Check for serverless / read-only environment like Vercel or AWS Lambda
            if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
                data_dir = os.path.join("/tmp", "auralife_data")
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                data_dir = os.path.join(base_dir, "data")
        
        self.data_dir = data_dir
        self.db_file = os.path.join(self.data_dir, "auralife_store.json")
        self.backup_dir = os.path.join(self.data_dir, "backups")
        
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(self.backup_dir, exist_ok=True)
        except OSError:
            # Fallback to /tmp if write permission denied in current filesystem
            self.data_dir = os.path.join("/tmp", "auralife_data")
            self.db_file = os.path.join(self.data_dir, "auralife_store.json")
            self.backup_dir = os.path.join(self.data_dir, "backups")
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(self.backup_dir, exist_ok=True)

        self.profile: UserProfile = UserProfile()
        self.tasks: List[Task] = []
        self.habits: List[Habit] = []
        self.expenses: List[Expense] = []
        self.notes: List[Note] = []

        self.load()

    def load(self):
        """Loads data from disk or seeds default initial data if none exists."""
        if not os.path.exists(self.db_file):
            # If in /tmp (e.g. Vercel), copy existing data store from repo if available
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            repo_db = os.path.join(base_dir, "data", "auralife_store.json")
            if os.path.exists(repo_db) and os.path.abspath(repo_db) != os.path.abspath(self.db_file):
                try:
                    shutil.copy2(repo_db, self.db_file)
                except Exception:
                    pass

        if not os.path.exists(self.db_file):
            self.seed_defaults()
            self.save()
            return

        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                payload = json.load(f)

            self.profile = UserProfile.from_dict(payload.get("profile", {}))
            self.tasks = [Task.from_dict(t) for t in payload.get("tasks", [])]
            self.habits = [Habit.from_dict(h) for h in payload.get("habits", [])]
            self.expenses = [Expense.from_dict(e) for e in payload.get("expenses", [])]
            self.notes = [Note.from_dict(n) for n in payload.get("notes", [])]
        except Exception as e:
            print(f"[Warning] Failed to load data store ({e}). Seeding defaults.")
            self.seed_defaults()
            self.save()

    def save(self):
        """Persists current state to JSON file and maintains a rolling backup."""
        payload = {
            "version": "1.0.0",
            "last_saved": datetime.now().isoformat(),
            "profile": self.profile.to_dict(),
            "tasks": [t.to_dict() for t in self.tasks],
            "habits": [h.to_dict() for h in self.habits],
            "expenses": [e.to_dict() for e in self.expenses],
            "notes": [n.to_dict() for n in self.notes],
        }

        # Save main file
        temp_file = self.db_file + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        
        if os.path.exists(self.db_file):
            # Backup previous copy
            backup_path = os.path.join(self.backup_dir, "auralife_store.backup.json")
            try:
                shutil.copyfile(self.db_file, backup_path)
            except Exception:
                pass

        shutil.move(temp_file, self.db_file)

    def seed_defaults(self):
        """Generates rich initial showcase data tailored for Shubhi Mathur."""
        today = date.today()
        
        self.profile = UserProfile(
            name="Shubhi Mathur",
            title="Software Creator & Product Innovator",
            monthly_budget=30000.0,
            focus_goal_minutes=150,
            pomodoro_work_min=25,
            pomodoro_break_min=5,
            theme="Dark Modern"
        )

        self.tasks = [
            Task(
                title="Review AuraLife Architecture & Design",
                description="Finalize modern UI layout, database schemas, and analytics engine",
                category="Project",
                priority="High",
                due_date=(today + timedelta(days=1)).isoformat(),
                completed=True,
                completed_at=datetime.now().isoformat()
            ),
            Task(
                title="Python Data Structures & Algorithms Practice",
                description="Solve 3 graph traversal problems and optimize space complexity",
                category="Study",
                priority="High",
                due_date=(today + timedelta(days=2)).isoformat(),
                completed=False
            ),
            Task(
                title="Prepare Product Portfolio Showcase",
                description="Document system design, key accomplishments, and interactive demos",
                category="Work",
                priority="Medium",
                due_date=(today + timedelta(days=4)).isoformat(),
                completed=False
            ),
            Task(
                title="Read 2 Chapters of Clean Architecture",
                description="Focus on dependency inversion and domain-driven design principles",
                category="Study",
                priority="Low",
                due_date=(today + timedelta(days=5)).isoformat(),
                completed=False
            ),
            Task(
                title="Evening 5K Run & Mindfulness",
                description="Maintain daily health cadence and mental clarity",
                category="Health",
                priority="Medium",
                due_date=today.isoformat(),
                completed=True,
                completed_at=datetime.now().isoformat()
            ),
        ]

        # Seed habit logs for past few days
        d0 = today.isoformat()
        d1 = (today - timedelta(days=1)).isoformat()
        d2 = (today - timedelta(days=2)).isoformat()
        d3 = (today - timedelta(days=3)).isoformat()

        self.habits = [
            Habit(
                name="Daily Python / Code Craft",
                category="Coding",
                logs=[d3, d2, d1, d0]
            ),
            Habit(
                name="Read Tech Tech & Books (30m)",
                category="Reading",
                logs=[d2, d1, d0]
            ),
            Habit(
                name="Drink 3L Water & Stay Hydrated",
                category="Wellness",
                logs=[d3, d2, d1, d0]
            ),
            Habit(
                name="Morning Meditation & Goal Review",
                category="Focus",
                logs=[d1, d0]
            ),
            Habit(
                name="Workout / Cardio Session",
                category="Fitness",
                logs=[d3, d1]
            ),
        ]

        self.expenses = [
            Expense(
                title="Cloud Server & API Credits",
                amount=1450.0,
                category="Tech",
                date=(today - timedelta(days=1)).isoformat(),
                notes="AI Model Inference testing"
            ),
            Expense(
                title="Specialty Coffee & Espresso Beans",
                amount=650.0,
                category="Food",
                date=today.isoformat(),
                notes="Focus fuel for development sprints"
            ),
            Expense(
                title="Python System Design Book",
                amount=1200.0,
                category="Books",
                date=(today - timedelta(days=4)).isoformat(),
                notes="Hardcover edition"
            ),
            Expense(
                title="High-Speed Fiber Internet Bill",
                amount=1899.0,
                category="Bills",
                date=(today - timedelta(days=6)).isoformat(),
                notes="Monthly home lab connectivity"
            ),
            Expense(
                title="Team Lunch & Networking",
                amount=1850.0,
                category="Food",
                date=(today - timedelta(days=3)).isoformat(),
                notes="Weekend developer meetup"
            ),
        ]

        self.notes = [
            Note(
                title="AuraLife Vision & Roadmap",
                category="Ideas",
                content=(
                    "# AuraLife Command Center\n"
                    "Created by Shubhi Mathur.\n\n"
                    "Key Goals:\n"
                    "1. Deliver lightning-fast productivity tracking without external bloat.\n"
                    "2. Enable deep focus with the integrated Pomodoro cycle.\n"
                    "3. Visualize financial discipline and habit streaks with intuitive charts.\n"
                    "4. Guarantee zero friction: runs everywhere with pure Python!"
                )
            ),
            Note(
                title="Favorite Python Design Patterns",
                category="Study",
                content=(
                    "1. Factory Method for extensible object instantiation.\n"
                    "2. Repository Pattern for decoupling data storage from business logic.\n"
                    "3. Observer Pattern for reactive UI updates.\n"
                    "4. Data classes for concise, readable domain models."
                )
            ),
            Note(
                title="Daily Affirmations & Focus Mantra",
                category="Wellness",
                content="Precision, consistency, and relentless curiosity create extraordinary outcomes."
            )
        ]

    # Task operations
    def add_task(self, task: Task) -> Task:
        self.tasks.append(task)
        self.save()
        return task

    def update_task(self, task: Task):
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks[i] = task
                break
        self.save()

    def delete_task(self, task_id: str) -> bool:
        initial_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        if len(self.tasks) != initial_len:
            self.save()
            return True
        return False

    def toggle_task(self, task_id: str) -> Optional[Task]:
        for t in self.tasks:
            if t.id == task_id:
                t.toggle()
                self.save()
                return t
        return None

    # Habit operations
    def add_habit(self, habit: Habit) -> Habit:
        self.habits.append(habit)
        self.save()
        return habit

    def toggle_habit_today(self, habit_id: str) -> Optional[bool]:
        for h in self.habits:
            if h.id == habit_id:
                res = h.log_today()
                self.save()
                return res
        return None

    def delete_habit(self, habit_id: str) -> bool:
        initial_len = len(self.habits)
        self.habits = [h for h in self.habits if h.id != habit_id]
        if len(self.habits) != initial_len:
            self.save()
            return True
        return False

    # Expense operations
    def add_expense(self, expense: Expense) -> Expense:
        self.expenses.append(expense)
        self.save()
        return expense

    def delete_expense(self, expense_id: str) -> bool:
        initial_len = len(self.expenses)
        self.expenses = [e for e in self.expenses if e.id != expense_id]
        if len(self.expenses) != initial_len:
            self.save()
            return True
        return False

    # Note operations
    def add_note(self, note: Note) -> Note:
        self.notes.append(note)
        self.save()
        return note

    def update_note(self, note: Note):
        for i, n in enumerate(self.notes):
            if n.id == note.id:
                note.updated_at = datetime.now().isoformat()
                self.notes[i] = note
                break
        self.save()

    def delete_note(self, note_id: str) -> bool:
        initial_len = len(self.notes)
        self.notes = [n for n in self.notes if n.id != note_id]
        if len(self.notes) != initial_len:
            self.save()
            return True
        return False

    # Profile operations
    def update_profile(self, profile: UserProfile):
        self.profile = profile
        self.save()
