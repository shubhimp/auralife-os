"""
Interactive CLI for AuraLife
Author: Shubhi Mathur
"""

import os
import sys
import time

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

from datetime import date
from core.database import DatabaseManager
from core.models import Task, Habit, Expense, Note
from core.analytics import AnalyticsEngine
from core.exporter import DataExporter


# ANSI color codes for enhanced terminal UX
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


class AuraLifeCLI:
    def __init__(self):
        self.db = DatabaseManager()
        self.analytics = AnalyticsEngine(self.db)
        self.exporter = DataExporter(self.db)

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def print_banner(self):
        print(f"{CYAN}{BOLD}")
        print(r"""
   ___                  __   _  __     
  / _ |__ _____ ___ _  / /  (_)/ /__   
 / __ / // / __/ _ `/ / /__/ // / -_)  
/_/ |_\_,_/_/  \_,_/ /____/_//_/\__/   
        """ + f"{RESET}")
        print(f"{MAGENTA}{BOLD}  * Personal Productivity & Command Center{RESET}")
        print(f"{GREEN}  * Created with Passion by: {BOLD}Shubhi Mathur{RESET}")
        print(f"{DIM}  " + "-" * 60 + f"{RESET}\n")

    def show_dashboard(self):
        self.clear()
        self.print_banner()

        score = self.analytics.calculate_productivity_score()
        task_m = self.analytics.get_task_metrics()
        habit_m = self.analytics.get_habit_metrics()
        fin_m = self.analytics.get_financial_metrics()

        # Score bar
        score_blocks = int(score / 5)
        bar = f"{GREEN}{'█' * score_blocks}{DIM}{'░' * (20 - score_blocks)}{RESET}"

        print(f"{BOLD}🎯 PRODUCTIVITY SCORE: {score}/100  [{bar}]{RESET}\n")

        print(f"{BOLD}{BLUE}┌─── 📋 TASK OVERVIEW ──────────────────────────────────────┐{RESET}")
        print(f"│  • Total Tasks: {task_m['total']:<4} | Completed: {GREEN}{task_m['completed']:<4}{RESET} | Pending: {YELLOW}{task_m['pending']:<4}{RESET} │")
        print(f"│  • Completion Rate: {CYAN}{task_m['completion_rate']}%{RESET} | High Priority Pending: {RED}{task_m['high_priority_pending']}{RESET}    │")
        print(f"{BOLD}{BLUE}└─── ⚡ HABIT STREAKS ───────────────────────────────────────┘{RESET}")
        print(f"│  • Checked Today: {GREEN}{habit_m['checked_today']}/{habit_m['total']}{RESET} ({habit_m['today_completion_rate']}%)                       │")
        print(f"│  • Top Streak: {YELLOW}{habit_m['best_streak']} Days{RESET} ({habit_m['best_habit'][:25]})            │")
        print(f"{BOLD}{BLUE}└─── 💰 FINANCIAL PULSE ────────────────────────────────────┘{RESET}")
        print(f"│  • Monthly Budget: ₹{fin_m['monthly_budget']:,.2f}                            │")
        print(f"│  • Spent: ₹{fin_m['total_spent']:,.2f} ({fin_m['budget_usage_pct']}%) | Remaining: ₹{fin_m['remaining_budget']:,.2f}       │")
        print(f"{BOLD}{BLUE}└────────────────────────────────────────────────────────────┘{RESET}\n")

        input(f"{DIM}Press Enter to return to menu...{RESET}")

    def manage_tasks(self):
        while True:
            self.clear()
            self.print_banner()
            print(f"{BOLD}{CYAN}=== 📋 TASK MANAGER ==={RESET}\n")

            if not self.db.tasks:
                print(f"{YELLOW}No tasks found. Add a task to get started!{RESET}\n")
            else:
                for idx, t in enumerate(self.db.tasks, 1):
                    status_icon = f"{GREEN}✔ DONE{RESET}" if t.completed else f"{YELLOW}○ TODO{RESET}"
                    pri_color = RED if t.priority == "High" else (YELLOW if t.priority == "Medium" else BLUE)
                    pri_tag = f"[{pri_color}{t.priority}{RESET}]"
                    print(f"{idx}. {status_icon} {pri_tag} {BOLD}{t.title}{RESET} ({CYAN}{t.category}{RESET}) Due: {t.due_date}")
                    if t.description:
                        print(f"     {DIM}↳ {t.description}{RESET}")
                print()

            print(f"{BOLD}[1]{RESET} Add Task  |  {BOLD}[2]{RESET} Toggle Complete  |  {BOLD}[3]{RESET} Delete Task  |  {BOLD}[0]{RESET} Back")
            choice = input(f"\n{BOLD}Select Option: {RESET}").strip()

            if choice == "1":
                title = input("Task Title: ").strip()
                if not title:
                    continue
                desc = input("Description (optional): ").strip()
                cat = input("Category (Work/Study/Project/Health/General) [General]: ").strip() or "General"
                pri = input("Priority (High/Medium/Low) [Medium]: ").strip().capitalize() or "Medium"
                if pri not in ["High", "Medium", "Low"]:
                    pri = "Medium"
                due = input(f"Due Date (YYYY-MM-DD) [{date.today().isoformat()}]: ").strip() or date.today().isoformat()
                self.db.add_task(Task(title=title, description=desc, category=cat, priority=pri, due_date=due))
                print(f"{GREEN}✓ Task added successfully!{RESET}")
                time.sleep(1)
            elif choice == "2":
                idx_str = input("Enter task number to toggle: ").strip()
                if idx_str.isdigit() and 1 <= int(idx_str) <= len(self.db.tasks):
                    task = self.db.tasks[int(idx_str) - 1]
                    self.db.toggle_task(task.id)
                    print(f"{GREEN}✓ Toggled '{task.title}'!{RESET}")
                    time.sleep(1)
            elif choice == "3":
                idx_str = input("Enter task number to delete: ").strip()
                if idx_str.isdigit() and 1 <= int(idx_str) <= len(self.db.tasks):
                    task = self.db.tasks[int(idx_str) - 1]
                    self.db.delete_task(task.id)
                    print(f"{RED}✓ Task deleted!{RESET}")
                    time.sleep(1)
            elif choice == "0":
                break

    def manage_habits(self):
        while True:
            self.clear()
            self.print_banner()
            print(f"{BOLD}{GREEN}=== ⚡ DAILY HABIT TRACKER ==={RESET}\n")

            for idx, h in enumerate(self.db.habits, 1):
                status = f"{GREEN}✔ Checked Today{RESET}" if h.is_logged_today() else f"{YELLOW}○ Pending{RESET}"
                streak = h.calculate_streak()
                print(f"{idx}. {BOLD}{h.name:<30}{RESET} [{CYAN}{h.category}{RESET}]  Streak: {YELLOW}{streak} days 🔥{RESET}  {status}")
            print()

            print(f"{BOLD}[1]{RESET} Check/Uncheck Habit Today  |  {BOLD}[2]{RESET} Add New Habit  |  {BOLD}[0]{RESET} Back")
            choice = input(f"\n{BOLD}Select Option: {RESET}").strip()

            if choice == "1":
                idx_str = input("Enter habit number to toggle: ").strip()
                if idx_str.isdigit() and 1 <= int(idx_str) <= len(self.db.habits):
                    h = self.db.habits[int(idx_str) - 1]
                    res = self.db.toggle_habit_today(h.id)
                    state = "Checked In" if res else "Unchecked"
                    print(f"{GREEN}✓ {state} for '{h.name}'!{RESET}")
                    time.sleep(1)
            elif choice == "2":
                name = input("Habit Name: ").strip()
                if not name:
                    continue
                cat = input("Category (Coding/Reading/Fitness/Wellness/Focus) [Wellness]: ").strip() or "Wellness"
                self.db.add_habit(Habit(name=name, category=cat))
                print(f"{GREEN}✓ New habit created!{RESET}")
                time.sleep(1)
            elif choice == "0":
                break

    def manage_expenses(self):
        while True:
            self.clear()
            self.print_banner()
            print(f"{BOLD}{YELLOW}=== 💰 EXPENSE & BUDGET TRACKER ==={RESET}\n")

            fin = self.analytics.get_financial_metrics()
            print(f"Monthly Budget: {BOLD}₹{fin['monthly_budget']:,.2f}{RESET}  |  Spent: {RED}₹{fin['total_spent']:,.2f}{RESET}  |  Remaining: {GREEN}₹{fin['remaining_budget']:,.2f}{RESET}")
            print(f"Budget Consumption: {fin['budget_usage_pct']}%\n")

            print(f"{BOLD}Recent Expenses:{RESET}")
            for idx, e in enumerate(self.db.expenses[-8:], 1):
                print(f" {idx}. {e.date} | ₹{e.amount:>8.2f} | {CYAN}{e.category:<8}{RESET} | {BOLD}{e.title}{RESET}")
            print()

            print(f"{BOLD}[1]{RESET} Add Expense  |  {BOLD}[2]{RESET} View Category Breakdown  |  {BOLD}[0]{RESET} Back")
            choice = input(f"\n{BOLD}Select Option: {RESET}").strip()

            if choice == "1":
                title = input("Expense Description: ").strip()
                amt_str = input("Amount (INR): ").strip()
                cat = input("Category (Food/Tech/Books/Bills/Travel/Other) [Food]: ").strip() or "Food"
                notes = input("Notes (optional): ").strip()
                try:
                    amt = float(amt_str)
                    self.db.add_expense(Expense(title=title, amount=amt, category=cat, notes=notes))
                    print(f"{GREEN}✓ Expense recorded!{RESET}")
                except ValueError:
                    print(f"{RED}Invalid amount.{RESET}")
                time.sleep(1)
            elif choice == "2":
                print(f"\n{BOLD}Category Breakdown:{RESET}")
                for cat, total in fin["categories"].items():
                    print(f" • {cat:<10}: ₹{total:,.2f}")
                input(f"\n{DIM}Press Enter to continue...{RESET}")
            elif choice == "0":
                break

    def run_pomodoro(self):
        self.clear()
        self.print_banner()
        print(f"{BOLD}{MAGENTA}=== ⏳ POMODORO FOCUS TIMER ==={RESET}\n")
        print(f"Creator Profile: {CYAN}{self.db.profile.name}{RESET}")
        print(f"Default Sprint: {self.db.profile.pomodoro_work_min} min focus | {self.db.profile.pomodoro_break_min} min break\n")
        
        mins = input(f"Enter minutes for this focus sprint [default {self.db.profile.pomodoro_work_min}]: ").strip()
        duration_min = int(mins) if mins.isdigit() else self.db.profile.pomodoro_work_min
        total_seconds = duration_min * 60

        print(f"\n{GREEN}🚀 Focus sprint started! Press Ctrl+C anytime to pause/stop.{RESET}\n")
        try:
            for rem in range(total_seconds, -1, -1):
                m, s = divmod(rem, 60)
                pct = int(((total_seconds - rem) / total_seconds) * 20)
                bar = f"{CYAN}{'█' * pct}{DIM}{'░' * (20 - pct)}{RESET}"
                sys.stdout.write(f"\r  ⏱ Time Remaining: {BOLD}{m:02d}:{s:02d}{RESET}  [{bar}] ")
                sys.stdout.flush()
                time.sleep(1)
            print(f"\n\n{GREEN}{BOLD}🎉 SPRINT COMPLETED! Great work, {self.db.profile.name}! Take a healthy break.{RESET}\n")
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}Sprint stopped by user.{RESET}\n")
        input(f"{DIM}Press Enter to return to menu...{RESET}")

    def manage_notes(self):
        while True:
            self.clear()
            self.print_banner()
            print(f"{BOLD}{BLUE}=== 📓 NOTES & BRAIN DUMP ==={RESET}\n")

            for idx, n in enumerate(self.db.notes, 1):
                print(f"{idx}. {BOLD}{n.title}{RESET} [{CYAN}{n.category}{RESET}] ({n.updated_at[:10]})")
            print()

            print(f"{BOLD}[1]{RESET} Read Note  |  {BOLD}[2]{RESET} Create New Note  |  {BOLD}[0]{RESET} Back")
            choice = input(f"\n{BOLD}Select Option: {RESET}").strip()

            if choice == "1":
                idx_str = input("Enter note number: ").strip()
                if idx_str.isdigit() and 1 <= int(idx_str) <= len(self.db.notes):
                    n = self.db.notes[int(idx_str) - 1]
                    print(f"\n{CYAN}{'═' * 50}{RESET}")
                    print(f"{BOLD}{n.title}{RESET} ({n.category})")
                    print(f"{DIM}Updated: {n.updated_at}{RESET}\n")
                    print(n.content)
                    print(f"{CYAN}{'═' * 50}{RESET}\n")
                    input(f"{DIM}Press Enter to continue...{RESET}")
            elif choice == "2":
                title = input("Note Title: ").strip()
                cat = input("Category [Ideas]: ").strip() or "Ideas"
                print("Enter note content (single line or paragraph):")
                content = input("> ")
                self.db.add_note(Note(title=title, category=cat, content=content))
                print(f"{GREEN}✓ Note saved!{RESET}")
                time.sleep(1)
            elif choice == "0":
                break

    def export_data(self):
        self.clear()
        self.print_banner()
        print(f"{BOLD}{CYAN}=== 📤 EXPORT & BACKUP ==={RESET}\n")
        f1 = self.exporter.export_tasks_csv()
        f2 = self.exporter.export_expenses_csv()
        f3 = self.exporter.export_full_json()

        print(f"{GREEN}✓ Exported Tasks CSV:{RESET} {f1}")
        print(f"{GREEN}✓ Exported Expenses CSV:{RESET} {f2}")
        print(f"{GREEN}✓ Exported Full JSON Backup:{RESET} {f3}\n")
        input(f"{DIM}Press Enter to return to menu...{RESET}")

    def show_profile(self):
        self.clear()
        self.print_banner()
        p = self.db.profile
        print(f"{BOLD}{MAGENTA}=== 👤 USER PROFILE & CREDITS ==={RESET}\n")
        print(f" • Name: {BOLD}{p.name}{RESET}")
        print(f" • Role: {p.title}")
        print(f" • Monthly Budget: ₹{p.monthly_budget:,.2f}")
        print(f" • Daily Focus Goal: {p.focus_goal_minutes} minutes")
        print(f" • Pomodoro Standard: {p.pomodoro_work_min}m focus / {p.pomodoro_break_min}m break\n")
        print(f"{GREEN}🌟 Crafted for Shubhi Mathur as a modern Python productivity system.{RESET}\n")
        input(f"{DIM}Press Enter to return to menu...{RESET}")

    def main_loop(self):
        while True:
            self.clear()
            self.print_banner()
            score = self.analytics.calculate_productivity_score()
            print(f" Welcome back, {BOLD}{self.db.profile.name}{RESET}! Daily Score: {GREEN}{score}/100{RESET}\n")
            print(f"  {BOLD}[1]{RESET} 📊 Dashboard & Metrics")
            print(f"  {BOLD}[2]{RESET} 📋 Task Manager")
            print(f"  {BOLD}[3]{RESET} ⚡ Daily Habits & Streaks")
            print(f"  {BOLD}[4]{RESET} 💰 Expense & Budget Tracker")
            print(f"  {BOLD}[5]{RESET} ⏳ Pomodoro Focus Timer")
            print(f"  {BOLD}[6]{RESET} 📓 Notes & Knowledge Journal")
            print(f"  {BOLD}[7]{RESET} 📤 Export Reports (CSV / JSON)")
            print(f"  {BOLD}[8]{RESET} 👤 Creator Profile & Settings")
            print(f"  {BOLD}[0]{RESET} 🚪 Exit AuraLife\n")

            choice = input(f"{BOLD}Select an option [0-8]: {RESET}").strip()
            if choice == "1":
                self.show_dashboard()
            elif choice == "2":
                self.manage_tasks()
            elif choice == "3":
                self.manage_habits()
            elif choice == "4":
                self.manage_expenses()
            elif choice == "5":
                self.run_pomodoro()
            elif choice == "6":
                self.manage_notes()
            elif choice == "7":
                self.export_data()
            elif choice == "8":
                self.show_profile()
            elif choice == "0":
                print(f"\n{CYAN}Have an inspiring and productive day, Shubhi Mathur! ✨{RESET}\n")
                break


def main():
    cli = AuraLifeCLI()
    cli.main_loop()


if __name__ == "__main__":
    main()
