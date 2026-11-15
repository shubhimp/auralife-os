"""
Productivity and Financial Analytics Engine for AuraLife
Author: Shubhi Mathur
"""

from datetime import date, timedelta
from typing import Dict, List, Any
from core.models import Task, Habit, Expense, UserProfile


class AnalyticsEngine:
    """Computes productivity metrics, financial health, and trend datasets."""

    def __init__(self, db):
        self.db = db

    def get_task_metrics(self) -> Dict[str, Any]:
        tasks = self.db.tasks
        total = len(tasks)
        if total == 0:
            return {
                "total": 0,
                "completed": 0,
                "pending": 0,
                "completion_rate": 0.0,
                "high_priority_pending": 0,
            }

        completed = sum(1 for t in tasks if t.completed)
        pending = total - completed
        rate = round((completed / total) * 100, 1)
        high_pending = sum(1 for t in tasks if not t.completed and t.priority == "High")

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": rate,
            "high_priority_pending": high_pending,
        }

    def get_habit_metrics(self) -> Dict[str, Any]:
        habits = self.db.habits
        total = len(habits)
        if total == 0:
            return {
                "total": 0,
                "checked_today": 0,
                "today_completion_rate": 0.0,
                "best_streak": 0,
                "best_habit": "None",
            }

        checked_today = sum(1 for h in habits if h.is_logged_today())
        rate = round((checked_today / total) * 100, 1)

        best_streak = 0
        best_habit = "None"
        for h in habits:
            streak = h.calculate_streak()
            if streak > best_streak:
                best_streak = streak
                best_habit = h.name

        return {
            "total": total,
            "checked_today": checked_today,
            "today_completion_rate": rate,
            "best_streak": best_streak,
            "best_habit": best_habit,
        }

    def get_financial_metrics(self) -> Dict[str, Any]:
        expenses = self.db.expenses
        budget = self.db.profile.monthly_budget
        today = date.today()
        current_month_prefix = f"{today.year}-{today.month:02d}"

        month_expenses = [
            e for e in expenses if e.date.startswith(current_month_prefix)
        ]
        total_spent = sum(e.amount for e in month_expenses)
        remaining = max(0.0, budget - total_spent)
        usage_pct = min(100.0, round((total_spent / budget) * 100, 1)) if budget > 0 else 0.0

        # Breakdown by category
        categories: Dict[str, float] = {}
        for e in month_expenses:
            categories[e.category] = categories.get(e.category, 0.0) + e.amount

        return {
            "monthly_budget": budget,
            "total_spent": round(total_spent, 2),
            "remaining_budget": round(remaining, 2),
            "budget_usage_pct": usage_pct,
            "categories": categories,
            "is_over_budget": total_spent > budget,
        }

    def calculate_productivity_score(self) -> int:
        """Calculates a holistic productivity score from 0 to 100."""
        task_met = self.get_task_metrics()
        habit_met = self.get_habit_metrics()

        task_factor = (task_met["completion_rate"] / 100.0) * 50  # Up to 50 points
        habit_factor = (habit_met["today_completion_rate"] / 100.0) * 35  # Up to 35 points
        streak_bonus = min(15, habit_met["best_streak"] * 3)  # Up to 15 bonus points

        total_score = int(round(task_factor + habit_factor + streak_bonus))
        return max(5, min(100, total_score))

    def get_last_7_days_activity(self) -> List[Dict[str, Any]]:
        """Returns 7-day completion timeline for visual graph rendering."""
        today = date.today()
        days_data = []

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.isoformat()
            day_label = day.strftime("%a")

            # Habit check-ins on this day
            habits_done = sum(1 for h in self.db.habits if day_str in h.logs)
            # Tasks completed on this day
            tasks_done = sum(
                1 for t in self.db.tasks
                if t.completed and t.completed_at and t.completed_at.startswith(day_str)
            )

            days_data.append({
                "date": day_str,
                "label": day_label,
                "habits_completed": habits_done,
                "tasks_completed": tasks_done,
                "total_points": (habits_done * 10) + (tasks_done * 15),
            })

        return days_data
