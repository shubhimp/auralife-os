# ⚡ AuraLife — Personal Command Center

> **Designed and Developed by: Shubhi Mathur**  
> *A modular, high-performance personal productivity and life cockpit crafted in Python.*

---

## 🌟 Overview

**AuraLife** is a complete, production-ready personal operating system built from scratch in pure Python. It combines task management, habit streak tracking, personal financial budgeting, a deep-work Pomodoro timer, and a markdown knowledge base into a unified dashboard.

Designed to be **approachable, lightning fast, and 100% self-contained**, AuraLife runs out of the box on standard Python with **zero external dependencies required**.

---

## 🚀 Key Features

| Module | Description |
| :--- | :--- |
| **📊 Smart Productivity Score** | Real-time 0–100 algorithm weighting completed tasks, daily habit check-ins, and active streaks. |
| **📋 Action Matrix (Tasks)** | Prioritized task management (High, Medium, Low) with categories, due dates, and completion status. |
| **⚡ Habit Streak Engine** | Daily consistency tracker with streak calculation, history logs, and motivational indicators. |
| **💰 Financial Pulse** | Monthly budget manager, expense logger, category distribution breakdown, and savings forecast. |
| **⏳ Pomodoro Focus Sprint** | 25-minute deep work cycles with animated countdown ring, pause/resume, and audio chime alerts. |
| **📓 Knowledge Brain Dump** | Fast note-taking system for ideas, architecture decisions, and learning summaries. |
| **📤 Local Data Exporter** | One-click CSV and JSON data export engine for complete data ownership and offline backup. |

---

## 🏗 System Architecture

```text
Shubhi's Python Project/
├── main.py                     # Primary entrypoint (auto-detects GUI/Web/CLI)
├── cli.py                      # Interactive ANSI terminal interface
├── gui.py                      # Desktop Tkinter GUI runner
├── requirements.txt            # Zero dependencies needed (pure stdlib)
├── run.bat                     # 1-click launcher for Windows
├── run_cli.bat                 # 1-click terminal launcher
├── run_tests.bat               # 1-click test suite runner
│
├── core/                       # Core domain logic
│   ├── models.py               # Data models: Task, Habit, Expense, Note, UserProfile
│   ├── database.py             # JSON repository with auto-seeding & rolling backups
│   ├── analytics.py            # Productivity score & financial calculation engine
│   └── exporter.py             # CSV / JSON report generator
│
├── web/                        # Built-in local web dashboard
│   ├── server.py               # Python native HTTP + REST API handler
│   └── index.html              # Modern dark-mode UI with live charts & audio
│
├── tests/                      # Automated unit test suite
│   ├── test_models.py          # Data structure validation
│   ├── test_database.py        # Persistence & CRUD tests
│   └── test_analytics.py       # Math & metrics verification
│
├── data/                       # Local persistent storage (auto-generated)
│   └── auralife_store.json
└── exports/                    # Exported CSV and JSON snapshots
```

---

## ⚡ 10-Minute Quickstart

### Option 1: Double-Click Launcher (Windows)
Simply double-click **`run.bat`** in the project folder!  
It starts the local server and automatically launches the modern dashboard in your web browser.

### Option 2: Command Line (PowerShell / Command Prompt)

1. **Launch the Dashboard**:
   ```bash
   python main.py
   ```

2. **Launch the Interactive Terminal CLI**:
   ```bash
   python main.py --cli
   # or
   python cli.py
   ```

3. **Run the Automated Test Suite (14 Tests)**:
   ```bash
   python main.py --test
   ```

4. **Export CSV & JSON Reports**:
   ```bash
   python main.py --export
   ```

---

## 💡 10-Minute Presentation & Showcase Guide

When explaining or demonstrating this project to reviewers, teachers, or colleagues:

1. **Explain the Architecture**:
   - Highlight separation of concerns: `core/models.py` (Domain Data), `core/database.py` (Persistence & Repository), `core/analytics.py` (Business Logic), and `web/` + `cli.py` (Presentation).
2. **Show the Algorithmic Logic**:
   - Point out `AnalyticsEngine.calculate_productivity_score()`:
     $$\text{Score} = (\text{Task \%} \times 0.50) + (\text{Habit \%} \times 0.35) + \min(15, \text{Streak} \times 3)$$
   - Point out `Habit.calculate_streak()` which dynamically traverses chronological ISO dates to handle consecutive active streaks.
3. **Demonstrate Data Persistence & Resilience**:
   - Show how `DatabaseManager` maintains atomic `.tmp` file writes and automatic rolling backups in `data/backups/`.
4. **Demonstrate Test Coverage**:
   - Run `python main.py --test` to show 14 unit tests passing in sub-second execution.

---

## 👤 Author & Acknowledgments

- **Creator & Lead Developer**: **Shubhi Mathur**
- **Project Name**: AuraLife Personal Command Center
- **License**: MIT Open Source License
