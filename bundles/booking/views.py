import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from core.date_picker import DatePicker
from core.time_picker import TimePicker

from bundles.booking.models import (
    create_booking,
    get_bookings_by_user,
    get_pending_bookings,
    get_all_bookings,
    approve_booking,
    reject_booking,
)
from bundles.equipment.models import get_all_laboratories
from core.validators import (
    validate_not_empty,
    validate_date_format,
    validate_time_format,
    validate_time_range,
)


# ---------------------------------------------------------------------------
# FR05 - Laboratory Booking (Student view)
# ---------------------------------------------------------------------------

class BookingStudentFrame(ttk.Frame):
    """Booking interface for students to request and view lab bookings."""

    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user

        # Laboratory lookup maps
        self._labs = []
        self._lab_names = []
        self._lab_id_map = {}

        self._build_form()
        self._build_treeview()
        self._load_laboratories()
        self._refresh_table()

        self.bind("<Visibility>", lambda _e: self._refresh_table())

    # ----- UI Construction ------------------------------------------------

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Request Laboratory Booking",
                              padding=10)
        form.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Row 0
        ttk.Label(form, text="Laboratory:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.lab_var = tk.StringVar()
        self.lab_combo = ttk.Combobox(form, textvariable=self.lab_var,
                                      state="readonly", width=30)
        self.lab_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(form, text="Date:").grid(
            row=0, column=2, sticky=tk.W, padx=5, pady=4)
        self.date_var = tk.StringVar()
        DatePicker(form, textvariable=self.date_var, width=15).grid(
            row=0, column=3, sticky=tk.W, padx=5, pady=4)

        # Row 1
        ttk.Label(form, text="Start Time:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=4)
        self.start_var = tk.StringVar(value="08:00")
        TimePicker(form, textvariable=self.start_var).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(form, text="End Time:").grid(
            row=1, column=2, sticky=tk.W, padx=5, pady=4)
        self.end_var = tk.StringVar(value="10:00")
        TimePicker(form, textvariable=self.end_var).grid(
            row=1, column=3, sticky=tk.W, padx=5, pady=4)

        # Row 2
        ttk.Label(form, text="Purpose:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=4)
        self.purpose_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.purpose_var, width=60).grid(
            row=2, column=1, columnspan=4, sticky=tk.W, padx=5, pady=4)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(btn_frame, text="Submit Booking",
                   command=self._on_submit, style="Green.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh Status",
                   command=self._refresh_table, style="Blue.TButton").pack(side=tk.LEFT, padx=5)

    def _build_treeview(self):
        lbl = ttk.Label(self, text="My Bookings", font=("", 10, "bold"))
        lbl.pack(anchor=tk.W, padx=10, pady=(10, 2))

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        columns = ("BookingID", "Laboratory", "Date", "Start", "End",
                   "Purpose", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=columns,
                                 show="headings", selectmode="browse")

        self.tree.heading("BookingID", text="Booking ID")
        self.tree.heading("Laboratory", text="Laboratory")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Start", text="Start")
        self.tree.heading("End", text="End")
        self.tree.heading("Purpose", text="Purpose")
        self.tree.heading("Status", text="Status")

        self.tree.column("BookingID", width=80, anchor=tk.CENTER)
        self.tree.column("Laboratory", width=150)
        self.tree.column("Date", width=100, anchor=tk.CENTER)
        self.tree.column("Start", width=70, anchor=tk.CENTER)
        self.tree.column("End", width=70, anchor=tk.CENTER)
        self.tree.column("Purpose", width=200)
        self.tree.column("Status", width=90, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ----- Data helpers ---------------------------------------------------

    def _load_laboratories(self):
        """Populate the laboratory combobox."""
        self._labs = get_all_laboratories()
        self._lab_names = [lab["LabName"] for lab in self._labs]
        self._lab_id_map = {lab["LabName"]: lab["LabID"]
                           for lab in self._labs}
        self.lab_combo["values"] = self._lab_names

    def _refresh_table(self):
        """Reload this student's bookings into the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for b in get_bookings_by_user(self.current_user["UserID"]):
            self.tree.insert("", tk.END, values=(
                b["BookingID"][:8] + "...",
                b["LabName"],
                b["BookingDate"],
                b["StartTime"],
                b["EndTime"],
                b.get("Purpose", ""),
                b["Status"],
            ))

    # ----- Validation -----------------------------------------------------

    def _validate_fields(self):
        """Validate all booking form fields.

        Returns (True, "") on success or (False, error_message).
        """
        if not self.lab_var.get():
            return False, "Please select a Laboratory."

        ok, msg = validate_date_format(self.date_var.get())
        if not ok:
            return False, msg

        ok, msg = validate_time_range(self.start_var.get(), self.end_var.get())
        if not ok:
            return False, msg

        ok, msg = validate_not_empty(self.purpose_var.get(), "Purpose")
        if not ok:
            return False, msg

        return True, ""

    # ----- Event handlers -------------------------------------------------

    def _on_submit(self):
        """Submit a new booking request."""
        ok, msg = self._validate_fields()
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return

        lab_id = self._lab_id_map.get(self.lab_var.get())
        success, result_msg = create_booking(
            self.current_user["UserID"],
            lab_id,
            self.date_var.get().strip(),
            self.start_var.get().strip(),
            self.end_var.get().strip(),
            self.purpose_var.get().strip(),
        )
        if success:
            messagebox.showinfo("Success", result_msg)
            # Clear form fields
            self.lab_var.set("")
            self.date_var.set(date.today().strftime("%Y-%m-%d"))
            self.start_var.set("08:00")
            self.end_var.set("10:00")
            self.purpose_var.set("")
            self._refresh_table()
        else:
            messagebox.showerror("Error", result_msg)


# ---------------------------------------------------------------------------
# FR05 - Laboratory Booking (Staff view)
# ---------------------------------------------------------------------------

class BookingStaffFrame(ttk.Frame):
    """Staff interface for approving / rejecting lab bookings."""

    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user

        self._build_pending_section()
        self._build_all_section()
        self._refresh_pending()
        self._refresh_all()

        self.bind("<Visibility>", lambda _e: self._on_refresh())

    # ----- UI Construction ------------------------------------------------

    def _build_pending_section(self):
        lbl = ttk.Label(self, text="Pending Booking Requests",
                        font=("", 10, "bold"))
        lbl.pack(anchor=tk.W, padx=10, pady=(10, 2))

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        columns = ("BookingID", "Student", "Laboratory", "Date",
                   "Start", "End", "Purpose", "Status")
        self.pending_tree = ttk.Treeview(tree_frame, columns=columns,
                                         show="headings",
                                         selectmode="browse")

        self.pending_tree.heading("BookingID", text="Booking ID")
        self.pending_tree.heading("Student", text="Student")
        self.pending_tree.heading("Laboratory", text="Laboratory")
        self.pending_tree.heading("Date", text="Date")
        self.pending_tree.heading("Start", text="Start")
        self.pending_tree.heading("End", text="End")
        self.pending_tree.heading("Purpose", text="Purpose")
        self.pending_tree.heading("Status", text="Status")

        self.pending_tree.column("BookingID", width=80, anchor=tk.CENTER)
        self.pending_tree.column("Student", width=130)
        self.pending_tree.column("Laboratory", width=140)
        self.pending_tree.column("Date", width=100, anchor=tk.CENTER)
        self.pending_tree.column("Start", width=60, anchor=tk.CENTER)
        self.pending_tree.column("End", width=60, anchor=tk.CENTER)
        self.pending_tree.column("Purpose", width=180)
        self.pending_tree.column("Status", width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                  command=self.pending_tree.yview)
        self.pending_tree.configure(yscrollcommand=scrollbar.set)

        self.pending_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(btn_frame, text="Approve Selected",
                   command=self._on_approve, style="Green.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reject Selected",
                   command=self._on_reject, style="Red.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh",
                   command=self._on_refresh, style="Blue.TButton").pack(side=tk.LEFT, padx=5)

    def _build_all_section(self):
        lbl = ttk.Label(self, text="All Bookings", font=("", 10, "bold"))
        lbl.pack(anchor=tk.W, padx=10, pady=(10, 2))

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        columns = ("BookingID", "Student", "Laboratory", "Date",
                   "Start", "End", "Purpose", "Status")
        self.all_tree = ttk.Treeview(tree_frame, columns=columns,
                                     show="headings", selectmode="browse")

        self.all_tree.heading("BookingID", text="Booking ID")
        self.all_tree.heading("Student", text="Student")
        self.all_tree.heading("Laboratory", text="Laboratory")
        self.all_tree.heading("Date", text="Date")
        self.all_tree.heading("Start", text="Start")
        self.all_tree.heading("End", text="End")
        self.all_tree.heading("Purpose", text="Purpose")
        self.all_tree.heading("Status", text="Status")

        self.all_tree.column("BookingID", width=80, anchor=tk.CENTER)
        self.all_tree.column("Student", width=130)
        self.all_tree.column("Laboratory", width=140)
        self.all_tree.column("Date", width=100, anchor=tk.CENTER)
        self.all_tree.column("Start", width=60, anchor=tk.CENTER)
        self.all_tree.column("End", width=60, anchor=tk.CENTER)
        self.all_tree.column("Purpose", width=180)
        self.all_tree.column("Status", width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                  command=self.all_tree.yview)
        self.all_tree.configure(yscrollcommand=scrollbar.set)

        self.all_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ----- Data helpers ---------------------------------------------------

    def _refresh_pending(self):
        """Reload pending bookings into the pending treeview."""
        self._pending_ids = []
        for item in self.pending_tree.get_children():
            self.pending_tree.delete(item)
        for b in get_pending_bookings():
            self._pending_ids.append(b["BookingID"])
            self.pending_tree.insert("", tk.END, values=(
                b["BookingID"][:8] + "...",
                b["StudentName"],
                b["LabName"],
                b["BookingDate"],
                b["StartTime"],
                b["EndTime"],
                b.get("Purpose", ""),
                b["Status"],
            ))

    def _refresh_all(self):
        """Reload all bookings into the all-bookings treeview."""
        for item in self.all_tree.get_children():
            self.all_tree.delete(item)
        for b in get_all_bookings():
            self.all_tree.insert("", tk.END, values=(
                b["BookingID"][:8] + "...",
                b["StudentName"],
                b["LabName"],
                b["BookingDate"],
                b["StartTime"],
                b["EndTime"],
                b.get("Purpose", ""),
                b["Status"],
            ))

    # ----- Event handlers -------------------------------------------------

    def _get_selected_booking_id(self):
        """Return the BookingID (full UUID) from the selected pending-tree row, or None."""
        selected = self.pending_tree.selection()
        if not selected:
            messagebox.showwarning("Warning",
                                   "Please select a booking request.")
            return None
        idx = self.pending_tree.index(selected[0])
        if idx < len(self._pending_ids):
            return self._pending_ids[idx]
        return None

    def _on_approve(self):
        """Approve the selected pending booking."""
        booking_id = self._get_selected_booking_id()
        if booking_id is None:
            return
        success, msg = approve_booking(
            booking_id, self.current_user["UserID"])
        if success:
            messagebox.showinfo("Success", msg)
            self._refresh_pending()
            self._refresh_all()
        else:
            messagebox.showerror("Error", msg)

    def _on_reject(self):
        """Reject the selected pending booking."""
        booking_id = self._get_selected_booking_id()
        if booking_id is None:
            return
        success, msg = reject_booking(
            booking_id, self.current_user["UserID"])
        if success:
            messagebox.showinfo("Success", msg)
            self._refresh_pending()
            self._refresh_all()
        else:
            messagebox.showerror("Error", msg)

    def _on_refresh(self):
        """Refresh both treeviews."""
        self._refresh_pending()
        self._refresh_all()
