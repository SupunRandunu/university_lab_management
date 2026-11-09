import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from bundles.user_management.models import (
    authenticate,
    get_all_users,
    add_user,
    update_user,
    delete_user,
    reset_password,
)
from core.validators import validate_not_empty, validate_email
from core.theme import (
    PRIMARY, PRIMARY_LIGHT, PRIMARY_DARK, ACCENT, WHITE,
    BG_LIGHT, TEXT_DARK, TEXT_LIGHT, draw_logo,
)


# ---------------------------------------------------------------------------
# Login Window
# ---------------------------------------------------------------------------

class LoginWindow(tk.Toplevel):
    """Themed login dialog with logo. Uses email as login credential."""

    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success

        self.title("Laboratory Management System")
        self.geometry("1100x650")
        self.resizable(False, False)
        self.configure(bg=WHITE)

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1100) // 2
        y = (self.winfo_screenheight() - 650) // 2
        self.geometry(f"+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_widgets()
        self.grab_set()
        self.email_entry.focus_set()

    def _build_widgets(self):
        # Centre container — holds all login content in the middle of the 1100x650 window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        center = tk.Frame(self, bg=WHITE, width=440)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Header bar
        header = tk.Frame(center, bg=PRIMARY, width=440, height=130)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Logo canvas
        logo_canvas = tk.Canvas(header, width=80, height=80,
                                bg=PRIMARY, highlightthickness=0)
        logo_canvas.pack(pady=(15, 5))
        draw_logo(logo_canvas, 40, 40, size=70)

        # Title in header
        tk.Label(header, text="Laboratory Management System",
                 font=("Segoe UI", 14, "bold"), bg=PRIMARY, fg=WHITE).pack()
        tk.Label(center, text="Sign in to your account",
                 font=("Segoe UI", 10), bg=WHITE, fg=TEXT_LIGHT).pack(pady=(15, 15))

        # Form
        form = tk.Frame(center, bg=WHITE)
        form.pack(padx=50, fill="x")

        # Email
        tk.Label(form, text="Email", font=("Segoe UI", 10, "bold"),
                 bg=WHITE, fg=TEXT_DARK).pack(anchor="w")
        self.email_entry = tk.Entry(form, font=("Segoe UI", 11),
                                    relief="solid", bd=1,
                                    highlightcolor=ACCENT, highlightthickness=1)
        self.email_entry.pack(fill="x", ipady=6, pady=(2, 12))

        # Password
        tk.Label(form, text="Password", font=("Segoe UI", 10, "bold"),
                 bg=WHITE, fg=TEXT_DARK).pack(anchor="w")
        self.password_entry = tk.Entry(form, font=("Segoe UI", 11), show="*",
                                       relief="solid", bd=1,
                                       highlightcolor=ACCENT, highlightthickness=1)
        self.password_entry.pack(fill="x", ipady=6, pady=(2, 20))

        # Login button
        login_btn = ttk.Button(form, text="Login", command=self._do_login,
                               style="Green.TButton", cursor="hand2")
        login_btn.pack(fill="x", ipady=4)

        # Key bindings
        self.email_entry.bind("<Return>", lambda e: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda e: self._do_login())

    def _do_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showerror(
                "Login Error", "Please enter both email and password.",
                parent=self,
            )
            return

        user_data = authenticate(email, password)
        if user_data is None:
            messagebox.showerror(
                "Login Error", "Invalid email or password.", parent=self
            )
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()
            return

        self.on_login_success(user_data)
        self.destroy()

    def _on_close(self):
        self.master.destroy()


# ---------------------------------------------------------------------------
# User Management Frame (Admin tab)
# ---------------------------------------------------------------------------

class UserManagementFrame(ttk.Frame):
    """Admin-only frame for creating, updating, and deleting users.
    Email is used as login credential (unique, required).
    Username is stored but NOT used for login."""

    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self._selected_user_id = None

        self._build_form()
        self._build_treeview()
        self._load_users()

    def _build_form(self):
        form_frame = ttk.LabelFrame(self, text="User Details", padding=10)
        form_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Row 0 -- Full Name & Username
        ttk.Label(form_frame, text="Full Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=3)
        self.fullname_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.fullname_var, width=30).grid(
            row=0, column=1, sticky="ew", padx=5, pady=3)

        ttk.Label(form_frame, text="Username:").grid(
            row=0, column=2, sticky="w", padx=5, pady=3)
        self.username_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.username_var, width=25).grid(
            row=0, column=3, sticky="ew", padx=5, pady=3)

        # Row 1 -- Email (Login) & Role
        ttk.Label(form_frame, text="Email (Login):").grid(
            row=1, column=0, sticky="w", padx=5, pady=3)
        self.email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.email_var, width=30).grid(
            row=1, column=1, sticky="ew", padx=5, pady=3)

        ttk.Label(form_frame, text="Role:").grid(
            row=1, column=2, sticky="w", padx=5, pady=3)
        self.role_var = tk.StringVar()
        self.role_combo = ttk.Combobox(
            form_frame, textvariable=self.role_var,
            values=["Student", "Staff", "Admin"],
            state="readonly", width=18)
        self.role_combo.grid(row=1, column=3, sticky="ew", padx=5, pady=3)

        # Row 2 -- Password & Index No
        ttk.Label(form_frame, text="Password:").grid(
            row=2, column=0, sticky="w", padx=5, pady=3)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            form_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=3)

        ttk.Label(form_frame, text="Index No:").grid(
            row=2, column=2, sticky="w", padx=5, pady=3)
        self.indexno_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.indexno_var, width=25).grid(
            row=2, column=3, sticky="ew", padx=5, pady=3)

        # Row 3 -- Contact No
        ttk.Label(form_frame, text="Contact No:").grid(
            row=3, column=0, sticky="w", padx=5, pady=3)
        self.contactno_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.contactno_var, width=30).grid(
            row=3, column=1, sticky="ew", padx=5, pady=3)

        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=(10, 0))

        ttk.Button(btn_frame, text="Add User", command=self._add_user, style="Green.TButton").pack(
            side="left", padx=5)
        ttk.Button(btn_frame, text="Update", command=self._update_user, style="Blue.TButton").pack(
            side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self._delete_user, style="Red.TButton").pack(
            side="left", padx=5)
        ttk.Button(btn_frame, text="Reset Password",
                   command=self._reset_password, style="Orange.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", command=self._clear_form, style="Grey.TButton").pack(
            side="left", padx=5)

    def _build_treeview(self):
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        columns = ("UserID", "FullName", "Username", "Email", "Role",
                   "IndexNo", "ContactNo")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", selectmode="browse")

        headings = {
            "UserID": "ID", "FullName": "Full Name", "Username": "Username",
            "Email": "Email (Login)", "Role": "Role",
            "IndexNo": "Index No", "ContactNo": "Contact No",
        }
        col_widths = {
            "UserID": 80, "FullName": 140, "Username": 100, "Email": 200,
            "Role": 80, "IndexNo": 100, "ContactNo": 120,
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=col_widths.get(col, 100), anchor="center")

        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for user in get_all_users():
            self.tree.insert("", "end", values=(
                user["UserID"][:8], user["FullName"],
                user.get("Username") or "", user.get("Email") or "",
                user["Role"],
                user.get("IndexNo") or "", user.get("ContactNo") or "",
            ))

    def _on_tree_select(self, _event):
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        # values[0] is truncated UserID (first 8 chars) -- find full ID
        truncated_id = values[0]
        for user in get_all_users():
            if user["UserID"][:8] == truncated_id:
                self._selected_user_id = user["UserID"]
                break
        self.fullname_var.set(values[1])
        self.username_var.set(values[2])
        self.email_var.set(values[3])
        self.role_var.set(values[4])
        self.indexno_var.set(values[5])
        self.contactno_var.set(values[6])
        self.password_var.set("")
        self.password_entry.configure(state="disabled")

    def _clear_form(self):
        self._selected_user_id = None
        self.fullname_var.set("")
        self.username_var.set("")
        self.email_var.set("")
        self.password_var.set("")
        self.role_var.set("")
        self.indexno_var.set("")
        self.contactno_var.set("")
        self.password_entry.configure(state="normal")
        self.tree.selection_remove(*self.tree.selection())

    def _validate_fields(self, require_password=False):
        ok, msg = validate_not_empty(self.fullname_var.get(), "Full Name")
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return False

        ok, msg = validate_not_empty(self.username_var.get(), "Username")
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return False

        ok, msg = validate_not_empty(self.email_var.get(), "Email")
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return False

        ok, msg = validate_email(self.email_var.get())
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return False

        if require_password:
            ok, msg = validate_not_empty(self.password_var.get(), "Password")
            if not ok:
                messagebox.showerror("Validation Error", msg)
                return False

        role = self.role_var.get()
        if role not in ("Student", "Staff", "Admin"):
            messagebox.showerror("Validation Error", "Please select a valid role.")
            return False

        if role == "Student":
            ok, msg = validate_not_empty(self.indexno_var.get(), "Index No")
            if not ok:
                messagebox.showerror("Validation Error", msg)
                return False

        return True

    def _add_user(self):
        if not self._validate_fields(require_password=True):
            return
        success, msg = add_user(
            full_name=self.fullname_var.get().strip(),
            username=self.username_var.get().strip(),
            email=self.email_var.get().strip(),
            password=self.password_var.get().strip(),
            role=self.role_var.get(),
            index_no=self.indexno_var.get().strip() or None,
            contact_no=self.contactno_var.get().strip() or None,
        )
        if success:
            messagebox.showinfo("Success", msg)
            self._clear_form()
            self._load_users()
        else:
            messagebox.showerror("Error", msg)

    def _update_user(self):
        if self._selected_user_id is None:
            messagebox.showerror("Error", "Please select a user to update.")
            return
        if not self._validate_fields(require_password=False):
            return
        success, msg = update_user(
            user_id=self._selected_user_id,
            full_name=self.fullname_var.get().strip(),
            username=self.username_var.get().strip(),
            email=self.email_var.get().strip(),
            role=self.role_var.get(),
            index_no=self.indexno_var.get().strip() or None,
            contact_no=self.contactno_var.get().strip() or None,
        )
        if success:
            messagebox.showinfo("Success", msg)
            self._clear_form()
            self._load_users()
        else:
            messagebox.showerror("Error", msg)

    def _delete_user(self):
        if self._selected_user_id is None:
            messagebox.showerror("Error", "Please select a user to delete.")
            return
        if self._selected_user_id == self.current_user["UserID"]:
            messagebox.showerror("Error", "You cannot delete your own account.")
            return
        confirm = messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this user?")
        if not confirm:
            return
        success, msg = delete_user(self._selected_user_id)
        if success:
            messagebox.showinfo("Success", msg)
            self._clear_form()
            self._load_users()
        else:
            messagebox.showerror("Error", msg)

    def _reset_password(self):
        if self._selected_user_id is None:
            messagebox.showerror("Error", "Please select a user first.")
            return
        new_pw = simpledialog.askstring(
            "Reset Password", "Enter new password:", show="*", parent=self)
        if not new_pw or not new_pw.strip():
            return
        success, msg = reset_password(self._selected_user_id, new_pw.strip())
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
