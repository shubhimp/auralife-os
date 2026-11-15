"""
Unit tests for database manager and persistence
Author: Shubhi Mathur
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
import shutil
import tempfile
from core.database import DatabaseManager
from core.models import Task, Habit, Expense, Note


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = DatabaseManager(data_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_default_seeding(self):
        self.assertGreater(len(self.db.tasks), 0)
        self.assertGreater(len(self.db.habits), 0)
        self.assertGreater(len(self.db.expenses), 0)
        self.assertEqual(self.db.profile.name, "Shubhi Mathur")

    def test_add_and_delete_task(self):
        initial_count = len(self.db.tasks)
        new_task = Task(title="Temporary Task", category="General")
        self.db.add_task(new_task)
        self.assertEqual(len(self.db.tasks), initial_count + 1)

        ok = self.db.delete_task(new_task.id)
        self.assertTrue(ok)
        self.assertEqual(len(self.db.tasks), initial_count)

    def test_toggle_task(self):
        task = self.db.tasks[0]
        initial_status = task.completed
        updated = self.db.toggle_task(task.id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.completed, not initial_status)

    def test_add_and_delete_expense(self):
        initial_count = len(self.db.expenses)
        new_exp = Expense(title="Keyboard", amount=2500.0, category="Tech")
        self.db.add_expense(new_exp)
        self.assertEqual(len(self.db.expenses), initial_count + 1)

        ok = self.db.delete_expense(new_exp.id)
        self.assertTrue(ok)
        self.assertEqual(len(self.db.expenses), initial_count)

    def test_persistence_across_instances(self):
        task = Task(title="Persistent Task Check")
        self.db.add_task(task)

        # Create new DB instance pointing to same test directory
        db2 = DatabaseManager(data_dir=self.test_dir)
        titles = [t.title for t in db2.tasks]
        self.assertIn("Persistent Task Check", titles)


if __name__ == "__main__":
    unittest.main()
