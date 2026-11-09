"""
Setup script for University Laboratory Management System.
Run this once to set up the environment and install dependencies.

Usage:
    python setup.py
"""

import subprocess
import sys
import os


def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(project_dir, "venv")
    requirements = os.path.join(project_dir, "requirements.txt")

    # Determine Python executable
    python = sys.executable

    print("=" * 60)
    print("  University Laboratory Management System - Setup")
    print("=" * 60)
    print()

    # Step 1: Create virtual environment
    if not os.path.exists(venv_dir):
        print("[1/3] Creating virtual environment...")
        subprocess.check_call([python, "-m", "venv", venv_dir])
        print("      Virtual environment created at: venv/")
    else:
        print("[1/3] Virtual environment already exists.")

    # Determine venv python/pip paths
    if sys.platform == "win32":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        venv_pip = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")
        venv_pip = os.path.join(venv_dir, "bin", "pip")

    # Step 2: Install dependencies
    print("[2/3] Installing dependencies from requirements.txt...")
    subprocess.check_call([venv_pip, "install", "--upgrade", "pip"],
                          stdout=subprocess.DEVNULL)
    subprocess.check_call([venv_pip, "install", "-r", requirements])
    print()

    # Step 3: Verify tkinter
    print("[3/3] Checking tkinter availability...")
    try:
        subprocess.check_call(
            [venv_python, "-c", "import tkinter; print('      tkinter version:', tkinter.TkVersion)"]
        )
    except subprocess.CalledProcessError:
        print()
        print("  WARNING: tkinter is NOT available in your Python installation.")
        print()
        if sys.platform == "darwin":
            print("  To fix on macOS, run:")
            print(f"    brew install python-tk@{sys.version_info.major}.{sys.version_info.minor}")
            print("  Then re-run: python setup.py")
        elif sys.platform == "linux":
            print("  To fix on Linux (Ubuntu/Debian), run:")
            print("    sudo apt-get install python3-tk")
            print("  To fix on Linux (Fedora/RHEL), run:")
            print("    sudo dnf install python3-tkinter")
        elif sys.platform == "win32":
            print("  Reinstall Python from python.org and check 'tcl/tk' during install.")
        print()
        sys.exit(1)

    print()
    print("=" * 60)
    print("  Setup complete!")
    print("=" * 60)
    print()
    print("  To run the application:")
    print()
    if sys.platform == "win32":
        print(f"    venv\\Scripts\\python main.py")
    else:
        print(f"    source venv/bin/activate")
        print(f"    python main.py")
    print()
    print("  Login credentials:")
    print("    Admin:   admin@uom.lk / admin123")
    print("    Staff:   john.smith@uom.lk / staff123")
    print("    Student: david.b@students.uom.lk / student123")
    print()


if __name__ == "__main__":
    main()
