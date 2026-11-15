"""
Unit tests for data models
Author: Shubhi Mathur
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from datetime import date, timedelta
from core.models import Task, Habit, Expense, Note, UserProfile


class TestModels(unittest.TestCase):
    def test_task_creation_and_toggle(self):
        task = Task(title="Build Portfolio", priority="High")
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)

        task.toggle()
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.completed_at)

        task.toggle()
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)

    def test_task_serialization(self):
        task = Task(title="Test Task", category="Study", priority="Low")
        d = task.to_dict()
        restored = Task.from_dict(d)
        self.assertEqual(restored.title, "Test Task")
        self.assertEqual(restored.priority, "Low")
        self.assertEqual(restored.category, "Study")

    def test_habit_streak_calculation(self):
        today = date.today()
        d0 = today.isoformat()
        d1 = (today - timedelta(days=1)).isoformat()
        d2 = (today - timedelta(days=2)).isoformat()

        habit = Habit(name="Read", logs=[d2, d1, d0])
        self.assertEqual(habit.calculate_streak(), 3)
        self.assertTrue(habit.is_logged_today())

        # Toggle today (uncheck)
        habit.log_today()
        self.assertFalse(habit.is_logged_today())
        # Since yesterday is still in logs, streak starting from yesterday is 2
        self.assertEqual(habit.calculate_streak(), 2)

    def test_expense_model(self):
        exp = Expense(title="Domain Name", amount=899.50, category="Tech")
        self.assertEqual(exp.amount, 899.50)
        self.assertEqual(exp.category, "Tech")
        d = exp.to_dict()
        self.assertEqual(d["title"], "Domain Name")

    def test_user_profile_defaults(self):
        profile = UserProfile()
        self.assertEqual(profile.name, "Shubhi Mathur")
        self.assertGreater(profile.monthly_budget, 0)


if __name__ == "__main__":
    unittest.main()
