import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk, messagebox

from core.date_picker import DatePicker

from bundles.borrowing.models import (
    borrow_equipment,
    return_equipment,
    get_active_borrowings,
)
from bundles.user_management.models import get_students
from bundles.equipment.models import get_all_equipment

BORROW_DAYS = 7


class BorrowingFrame(ttk.Frame):
    """Staff interface for issuing and returning equipment (FR04)."""

    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user

        self._build_top_panels()
        self._build_treeview()
        self._load_combos()
        self._refresh_table()

        self.bind("<Visibility>", lambda _e: self._refresh_all())

    # ----- UI Construction ------------------------------------------------

    def _build_top_panels(self):
        """Build the Issue and Return LabelFrames side by side."""
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=(10, 5))

        # --- Left: Issue Equipment ----------------------------------------
        issue_frame = ttk.LabelFrame(top, text="Issue Equipment", padding=10)
        issue_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(issue_frame, text="Student:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(
            issue_frame, textvariable=self.student_var,
            state="readonly", width=30)
        self.student_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=4)
        self.student_combo.bind("<ButtonPress>", self._load_students)

        ttk.Label(issue_frame, text="Equipment:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=4)
        self.equip_var = tk.StringVar()
        self.equip_combo = ttk.Combobox(
            issue_frame, textvariable=self.equip_var,
            state="readonly", width=30)
        self.equip_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=4)
        self.equip_combo.bind("<ButtonPress>", self._load_equipment)

        ttk.Label(issue_frame, text="Borrow Date:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=4)
        self.borrow_date_var = tk.StringVar(value=date.today().isoformat())
        DatePicker(issue_frame, textvariable=self.borrow_date_var,
                   width=15).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(issue_frame, text="Due Date:").grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=4)
        due = date.today() + timedelta(days=BORROW_DAYS)
        self.due_date_var = tk.StringVar(value=due.isoformat())
        ttk.Label(issue_frame, textvariable=self.due_date_var).grid(
            row=3, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Button(issue_frame, text="Issue Equipment",
                   command=self._on_issue, style="Green.TButton").grid(
            row=4, column=0, columnspan=2, pady=(8, 0))

        # --- Right: Return Equipment --------------------------------------
        return_frame = ttk.LabelFrame(top, text="Return Equipment", padding=10)
        return_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Label(return_frame, text="Equipment:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.return_eq_var = tk.StringVar()
        self.return_eq_combo = ttk.Combobox(
            return_frame, textvariable=self.return_eq_var,
            state="readonly", width=30)
        self.return_eq_combo.grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=4)
        self.return_eq_combo.bind("<ButtonPress>", self._load_return_equipment)

        ttk.Label(
            return_frame,
            text="Select from table below or choose from dropdown",
            foreground="grey",
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        ttk.Button(return_frame, text="Return Equipment",
                   command=self._on_return, style="Orange.TButton").grid(
            row=2, column=0, columnspan=2, pady=(8, 0))

    def _build_treeview(self):
        """Build the Active Borrowings treeview at the bottom."""
        lf = ttk.LabelFrame(self, text="Active Borrowings", padding=5)
        lf.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        columns = ("EquipmentID", "EquipmentName", "Student",
                   "BorrowDate", "DueDate")
        self.tree = ttk.Treeview(lf, columns=columns,
                                 show="headings", selectmode="browse")

        self.tree.heading("EquipmentID", text="Equipment ID")
        self.tree.heading("EquipmentName", text="Equipment Name")
        self.tree.heading("Student", text="Student")
        self.tree.heading("BorrowDate", text="Borrow Date")
        self.tree.heading("DueDate", text="Due Date")

        self.tree.column("EquipmentID", width=100, anchor=tk.CENTER)
        self.tree.column("EquipmentName", width=180)
        self.tree.column("Student", width=160)
        self.tree.column("BorrowDate", width=110, anchor=tk.CENTER)
        self.tree.column("DueDate", width=110, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(lf, orient=tk.VERTICAL,
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

    # ----- Data helpers ---------------------------------------------------

    def _load_combos(self):
        """Populate all comboboxes."""
        self._load_students()
        self._load_equipment()
        self._load_return_equipment()

    def _load_students(self, _event=None):
        """Refresh the student combobox from the database."""
        students = get_students()
        self._student_map = {}
        student_values = []
        for s in students:
            display = f"{s['FullName']} ({s['Email']})"
            student_values.append(display)
            self._student_map[display] = s["UserID"]
        self.student_combo["values"] = student_values

    def _load_equipment(self, _event=None):
        """Refresh the equipment combobox (available only) from the database."""
        all_eq = get_all_equipment()
        self._equip_map = {}
        equip_values = []
        for eq in all_eq:
            if eq["Status"] == "Available":
                display = eq["Name"]
                equip_values.append(display)
                self._equip_map[display] = eq["EquipmentID"]
        self.equip_combo["values"] = equip_values

    def _load_return_equipment(self, _event=None):
        """Refresh the return equipment combobox from the database."""
        self._return_equip_map = {}
        active = get_active_borrowings()
        return_values = []
        for b in active:
            display = f"{b['EquipmentName']} ({b['EquipmentID'][:8]}...)"
            return_values.append(display)
            self._return_equip_map[display] = b["EquipmentID"]
        self.return_eq_combo["values"] = return_values

    def _refresh_table(self):
        """Reload active borrowings into the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for b in get_active_borrowings():
            self.tree.insert("", tk.END, values=(
                b["EquipmentID"][:8] + "...",
                b["EquipmentName"],
                b["StudentName"],
                b["BorrowDate"],
                b["DueDate"],
            ))

    def _refresh_all(self):
        """Refresh both the treeview and the comboboxes."""
        self._load_combos()
        self._refresh_table()

    # ----- Event handlers -------------------------------------------------

    def _on_row_select(self, _event=None):
        """Populate the return equipment combobox from the selected row."""
        selected = self.tree.selection()
        if not selected:
            return
        idx = self.tree.index(selected[0])
        values = self.return_eq_combo["values"]
        if idx < len(values):
            self.return_eq_var.set(values[idx])

    def _on_issue(self):
        """Validate and issue equipment to a student."""
        student_display = self.student_var.get()
        equip_display = self.equip_var.get()

        if not student_display:
            messagebox.showerror("Validation Error",
                                 "Please select a student.")
            return
        if not equip_display:
            messagebox.showerror("Validation Error",
                                 "Please select equipment.")
            return

        user_id = self._student_map.get(student_display)
        equipment_id = self._equip_map.get(equip_display)
        borrow_date = self.borrow_date_var.get().strip()
        due_date = self.due_date_var.get().strip()

        if not borrow_date:
            messagebox.showerror("Validation Error",
                                 "Borrow date is required.")
            return

        issued_by = self.current_user["UserID"]

        success, msg = borrow_equipment(
            user_id, equipment_id, issued_by, borrow_date, due_date)

        if success:
            messagebox.showinfo("Success", msg)
            self.student_var.set("")
            self.equip_var.set("")
            self.borrow_date_var.set(date.today().isoformat())
            due = date.today() + timedelta(days=BORROW_DAYS)
            self.due_date_var.set(due.isoformat())
            self._refresh_all()
        else:
            messagebox.showerror("Error", msg)

    def _on_return(self):
        """Return equipment, asking whether it is damaged."""
        return_display = self.return_eq_var.get().strip()
        if not return_display:
            messagebox.showerror("Validation Error",
                                 "Please select an equipment item to return.")
            return

        equipment_id = self._return_equip_map.get(return_display)
        if not equipment_id:
            messagebox.showerror("Validation Error",
                                 "Could not find the selected equipment.")
            return

        is_damaged = messagebox.askyesno(
            "Return Condition",
            "Is the equipment damaged?")

        return_date = date.today().isoformat()
        staff_id = self.current_user["UserID"]

        success, msg = return_equipment(
            equipment_id, return_date, is_damaged, staff_id)

        if success:
            messagebox.showinfo("Success", msg)
            self.return_eq_var.set("")
            self._refresh_all()
        else:
            messagebox.showerror("Error", msg)
