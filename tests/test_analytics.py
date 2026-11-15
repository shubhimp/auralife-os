"""
Unit tests for analytics engine
Author: Shubhi Mathur
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
import shutil
import tempfile
from core.database import DatabaseManager
from core.analytics import AnalyticsEngine
from core.models import Task, Habit, Expense


class TestAnalyticsEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = DatabaseManager(data_dir=self.test_dir)
        self.analytics = AnalyticsEngine(self.db)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_task_metrics(self):
        metrics = self.analytics.get_task_metrics()
        self.assertIn("total", metrics)
        self.assertIn("completed", metrics)
        self.assertIn("completion_rate", metrics)
        self.assertEqual(metrics["total"], metrics["completed"] + metrics["pending"])

    def test_financial_metrics(self):
        metrics = self.analytics.get_financial_metrics()
        self.assertGreater(metrics["monthly_budget"], 0)
        self.assertGreaterEqual(metrics["total_spent"], 0)
        self.assertIn("categories", metrics)

    def test_productivity_score_range(self):
        score = self.analytics.calculate_productivity_score()
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_7_day_activity_structure(self):
        activity = self.analytics.get_last_7_days_activity()
        self.assertEqual(len(activity), 7)
        self.assertIn("label", activity[0])
        self.assertIn("total_points", activity[0])


if __name__ == "__main__":
    unittest.main()
