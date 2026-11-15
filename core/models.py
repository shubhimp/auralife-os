"""
Data models for AuraLife
Author: Shubhi Mathur
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import uuid


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    category: str = "General"  # Work, Study, Project, Health, General
    priority: str = "Medium"   # High, Medium, Low
    due_date: str = field(default_factory=lambda: date.today().isoformat())
    completed: bool = False
    completed_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def toggle(self):
        self.completed = not self.completed
        self.completed_at = datetime.now().isoformat() if self.completed else None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(**data)


@dataclass
class Habit:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    category: str = "Wellness"  # Coding, Reading, Wellness, Fitness, Focus
    target_frequency: str = "Daily"
    logs: List[str] = field(default_factory=list)  # ISO Date strings: YYYY-MM-DD
    created_at: str = field(default_factory=lambda: date.today().isoformat())

    def log_today(self) -> bool:
        today = date.today().isoformat()
        if today in self.logs:
            self.logs.remove(today)
            return False
        else:
            self.logs.append(today)
            self.logs.sort()
            return True

    def is_logged_today(self) -> bool:
        return date.today().isoformat() in self.logs

    def calculate_streak(self) -> int:
        if not self.logs:
            return 0
        
        log_set = set(self.logs)
        today = date.today()
        streak = 0
        curr = today
        
        # If not logged today yet, check starting from yesterday
        if curr.isoformat() not in log_set:
            curr = curr - timedelta(days=1)
            
        while curr.isoformat() in log_set:
            streak += 1
            curr = curr - timedelta(days=1)
            
        return streak

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Habit":
        return cls(**data)


@dataclass
class Expense:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    amount: float = 0.0
    category: str = "Food"  # Food, Tech, Books, Travel, Bills, Other
    date: str = field(default_factory=lambda: date.today().isoformat())
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        return cls(**data)


@dataclass
class Note:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    content: str = ""
    category: str = "Ideas"
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(**data)


@dataclass
class UserProfile:
    name: str = "Shubhi Mathur"
    title: str = "Lead Creator & Software Enthusiast"
    monthly_budget: float = 25000.0
    focus_goal_minutes: int = 120
    pomodoro_work_min: int = 25
    pomodoro_break_min: int = 5
    theme: str = "Dark Modern"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        return cls(**data)
