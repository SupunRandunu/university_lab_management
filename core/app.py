import tkinter as tk
from tkinter import ttk

from core.bundle_manager import BundleManager
from core.logger import get_logger
from core.theme import apply_theme, PRIMARY, WHITE

log = get_logger("core.app")

MAIN_WINDOW_SIZE = "1100x650"
ROLE_STAFF = "Staff"
ROLE_ADMIN = "Admin"


class Application:
    """Main application controller.

    Bootstraps bundles, initialises the database, shows the login window,
    and builds the role-appropriate main interface on successful login.
    """

    def __init__(self):
        self.bundle_manager = BundleManager()
        self.bundle_manager.discover_bundles()
        self.bundle_manager.initialize_database()
        log.info("Bundle manager initialized, %d bundles loaded", len(self.bundle_manager.bundles))

        self.root = tk.Tk()
        apply_theme(self.root)
        self.root.withdraw()
        self._show_login()

    # ------------------------------------------------------------------
    # Login / logout
    # ------------------------------------------------------------------

    def _show_login(self):
        # Import here to avoid circular imports
        from bundles.user_management.views import LoginWindow

        LoginWindow(self.root, self._on_login_success)

    def _on_login_success(self, user_data):
        log.info("User logged in: %s (%s) [%s]", user_data["FullName"], user_data["Role"], user_data["Email"])
        self.root.geometry(MAIN_WINDOW_SIZE)
        self.root.resizable(False, False)
        self.root.deiconify()
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")

        role = user_data["Role"]
        if role in (ROLE_STAFF, ROLE_ADMIN):
            self._build_staff_window(user_data)
        else:
            self._build_student_window(user_data)

    def _on_logout(self):
        log.info("User logged out")
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.withdraw()
        self._show_login()

    # ------------------------------------------------------------------
    # Window builders
    # ------------------------------------------------------------------

    def _build_staff_window(self, user_data):
        self.root.title(
            f"Laboratory Management System - {user_data['Role']}: {user_data['FullName']}"
        )

        top_frame = tk.Frame(self.root, bg=PRIMARY, padx=10, pady=8)
        top_frame.pack(fill="x")
        tk.Label(
            top_frame,
            text=f"  Logged in as: {user_data['FullName']}  ({user_data['Role']})",
            font=("Segoe UI", 11), bg=PRIMARY, fg=WHITE,
        ).pack(side="left")
        ttk.Button(top_frame, text="  Logout  ", command=self._on_logout,
                   style="Red.TButton", cursor="hand2").pack(side="right")

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Add staff tabs from all bundles
        tabs = list(self.bundle_manager.get_staff_tabs(notebook, user_data))
        log.debug("Building staff window with %d tabs", len(tabs))
        for label, frame in tabs:
            notebook.add(frame, text=f"  {label}  ")

        # Add admin-only tabs if user is Admin
        if user_data["Role"] == ROLE_ADMIN:
            for label, frame in self.bundle_manager.get_admin_tabs(
                notebook, user_data
            ):
                notebook.add(frame, text=f"  {label}  ")

    def _build_student_window(self, user_data):
        self.root.title(
            f"Laboratory Management System - Student: {user_data['FullName']}"
        )

        top_frame = tk.Frame(self.root, bg=PRIMARY, padx=10, pady=8)
        top_frame.pack(fill="x")
        tk.Label(
            top_frame,
            text=f"  Logged in as: {user_data['FullName']}  ({user_data['Role']})",
            font=("Segoe UI", 11), bg=PRIMARY, fg=WHITE,
        ).pack(side="left")
        ttk.Button(top_frame, text="  Logout  ", command=self._on_logout,
                   style="Red.TButton", cursor="hand2").pack(side="right")

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        tabs = list(self.bundle_manager.get_student_tabs(notebook, user_data))
        log.debug("Building student window with %d tabs", len(tabs))
        for label, frame in tabs:
            notebook.add(frame, text=f"  {label}  ")

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self):
        self.root.mainloop()
