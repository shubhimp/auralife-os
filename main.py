"""
AuraLife - The All-In-One Personal Command Center
Author: Shubhi Mathur
Year: 2026

Entry point for launching AuraLife across GUI, Web, and CLI interfaces.
"""

import sys
import os

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

from core.database import DatabaseManager
from core.analytics import AnalyticsEngine
from core.exporter import DataExporter


def print_welcome_banner():
    print("\n" + "=" * 65)
    print("   * AuraLife Personal Productivity & Command Center *")
    print("   * Created with Passion by: Shubhi Mathur")
    print("   * Version: 1.0.0 | Pure Python Architecture")
    print("=" * 65 + "\n")


def run_tests():
    import unittest
    print("[AuraLife Test Runner] Discovering and executing unit tests...")
    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


def export_now():
    db = DatabaseManager()
    exporter = DataExporter(db)
    print("[AuraLife Exporter] Generating data exports...")
    t = exporter.export_tasks_csv()
    e = exporter.export_expenses_csv()
    b = exporter.export_full_json()
    print(f" ✓ Tasks CSV: {t}")
    print(f" ✓ Expenses CSV: {e}")
    print(f" ✓ Backup JSON: {b}")
    print("\nAll files successfully exported to 'exports/' folder.")


def main():
    print_welcome_banner()

    args = sys.argv[1:]

    if "--test" in args or "-t" in args:
        run_tests()
        return

    if "--export" in args:
        export_now()
        return

    if "--cli" in args or "-c" in args:
        from cli import AuraLifeCLI
        cli = AuraLifeCLI()
        cli.main_loop()
        return

    # Default mode: Launch modern interactive GUI dashboard
    print("🚀 Initializing AuraLife Modern Interactive Cockpit...")
    print("💡 Tip: You can also run 'python main.py --cli' for the terminal interface.")
    print("💡 Tip: You can run 'python main.py --test' to run the test suite.\n")

    # Check for Tkinter or start web cockpit
    try:
        import tkinter
        # If Tkinter is installed and functional, we can offer choice or launch web
        from web.server import start_web_server
        start_web_server(port=5000, open_browser=True)
    except (ImportError, Exception):
        from web.server import start_web_server
        start_web_server(port=5000, open_browser=True)


if __name__ == "__main__":
    main()
