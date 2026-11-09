"""
Laboratory Management System
Entry point - initializes bundles and launches the application.

Bundle Architecture:
    Each feature is a self-contained bundle in the bundles/ directory.
    To add a new feature: create a new folder in bundles/ with __init__.py,
    models.py, and views.py. The bundle is auto-discovered on startup.
    To remove a feature: delete its folder from bundles/.
"""

import sys
import os

# Add project root to Python path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_dependencies():
    """Verify all required packages are installed before starting."""
    missing = []

    try:
        import tkinter  # noqa: F401
    except ImportError:
        print("ERROR: tkinter is not installed.")
        if sys.platform == "darwin":
            v = f"{sys.version_info.major}.{sys.version_info.minor}"
            print(f"  Fix: brew install python-tk@{v}")
        elif sys.platform == "linux":
            print("  Fix: sudo apt-get install python3-tk")
        elif sys.platform == "win32":
            print("  Fix: reinstall Python from python.org with tcl/tk checked")
        sys.exit(1)

    try:
        import fpdf  # noqa: F401
    except ImportError:
        missing.append("fpdf2")

    try:
        import PIL  # noqa: F401
    except ImportError:
        missing.append("Pillow")

    if missing:
        print("ERROR: Missing required packages:", ", ".join(missing))
        print()
        print("  Run one of:")
        print("    python setup.py              (recommended - sets up everything)")
        print("    pip install -r requirements.txt   (if venv is already active)")
        sys.exit(1)


def main():
    check_dependencies()

    from core.logger import setup_logging, get_logger
    setup_logging()
    log = get_logger("main")

    log.info("=" * 60)
    log.info("Laboratory Management System starting")
    log.info("=" * 60)

    from core.app import Application
    app = Application()
    app.run()
    log.info("Application closed")


if __name__ == "__main__":
    main()
