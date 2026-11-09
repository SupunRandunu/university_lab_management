import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.date_picker import DatePicker

from bundles.reports.models import (
    get_equipment_report,
    get_borrowing_report,
    get_returning_report,
    get_booking_report,
    get_maintenance_report,
    generate_pdf,
)
from core.validators import validate_date_format


# ---------------------------------------------------------------------------
# Column definitions for each report type
# ---------------------------------------------------------------------------

REPORT_COLUMNS = {
    "Equipment": {
        "headers": ["Equipment ID", "Name", "Category", "Lab Name",
                     "Purchase Date", "Status"],
        "keys": ["EquipmentID", "Name", "Category", "LabName",
                 "PurchaseDate", "Status"],
    },
    "Borrowing": {
        "headers": ["Borrow ID", "Student", "Equipment", "Borrow Date",
                     "Due Date", "Return Date", "Condition"],
        "keys": ["BorrowID", "StudentName", "EquipmentName", "BorrowDate",
                 "DueDate", "ReturnDate", "ReturnCondition"],
    },
    "Returning": {
        "headers": ["Borrow ID", "Student", "Equipment", "Borrow Date",
                     "Due Date", "Return Date", "Condition"],
        "keys": ["BorrowID", "StudentName", "EquipmentName", "BorrowDate",
                 "DueDate", "ReturnDate", "ReturnCondition"],
    },
    "Booking": {
        "headers": ["Booking ID", "Student", "Lab Name", "Booking Date",
                     "Start Time", "End Time", "Purpose", "Status"],
        "keys": ["BookingID", "StudentName", "LabName", "BookingDate",
                 "StartTime", "EndTime", "Purpose", "Status"],
    },
    "Maintenance": {
        "headers": ["Maintenance ID", "Equipment", "Issue", "Reported By",
                     "Reported Date", "Completed Date", "Remarks", "Status"],
        "keys": ["MaintenanceID", "EquipmentName", "IssueDescription",
                 "ReportedByName", "ReportedDate", "CompletedDate",
                 "Remarks", "Status"],
    },
}

REPORT_FUNCTIONS = {
    "Equipment": get_equipment_report,
    "Borrowing": get_borrowing_report,
    "Returning": get_returning_report,
    "Booking": get_booking_report,
    "Maintenance": get_maintenance_report,
}


# ---------------------------------------------------------------------------
# Report GUI
# ---------------------------------------------------------------------------

class ReportFrame(ttk.Frame):
    """Interface for generating and exporting date-range reports (staff only)."""

    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self._current_data = []       # raw row tuples for export
        self._current_headers = []    # header strings for export
        self._current_title = ""

        self._build_controls()
        self._build_treeview()

    # ----- UI Construction ------------------------------------------------

    def _build_controls(self):
        ctrl = ttk.LabelFrame(self, text="Generate Report", padding=10)
        ctrl.pack(fill=tk.X, padx=10, pady=(10, 5))

        ttk.Label(ctrl, text="Report Type:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(ctrl, textvariable=self.type_var,
                                  state="readonly", width=20,
                                  values=list(REPORT_COLUMNS.keys()))
        type_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=4)
        type_combo.current(0)

        ttk.Label(ctrl, text="From Date:").grid(
            row=0, column=2, sticky=tk.W, padx=5, pady=4)
        self.from_var = tk.StringVar(value="2020-01-01")
        DatePicker(ctrl, textvariable=self.from_var, width=12).grid(
            row=0, column=3, sticky=tk.W, padx=5, pady=4)

        ttk.Label(ctrl, text="To Date:").grid(
            row=0, column=4, sticky=tk.W, padx=5, pady=4)
        self.to_var = tk.StringVar(value="2030-12-31")
        DatePicker(ctrl, textvariable=self.to_var, width=12).grid(
            row=0, column=5, sticky=tk.W, padx=5, pady=4)

        ttk.Button(ctrl, text="Generate",
                   command=self._on_generate, style="Blue.TButton").grid(
            row=0, column=6, padx=10, pady=4)
        ttk.Button(ctrl, text="Export PDF",
                   command=self._on_export_pdf, style="Green.TButton").grid(
            row=0, column=7, padx=5, pady=4)

    def _build_treeview(self):
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        self.tree = ttk.Treeview(tree_frame, show="headings",
                                 selectmode="browse")

        self.v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                      command=self.tree.yview)
        self.h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL,
                                      command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.v_scroll.set,
                            xscrollcommand=self.h_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

    # ----- Actions --------------------------------------------------------

    def _on_generate(self):
        """Fetch data for the selected report type and date range."""
        report_type = self.type_var.get()
        if not report_type:
            messagebox.showwarning("Warning", "Please select a report type.")
            return

        from_date = self.from_var.get().strip()
        to_date = self.to_var.get().strip()

        ok, msg = validate_date_format(from_date)
        if not ok:
            messagebox.showerror("Validation Error", f"From Date: {msg}")
            return
        ok, msg = validate_date_format(to_date)
        if not ok:
            messagebox.showerror("Validation Error", f"To Date: {msg}")
            return

        func = REPORT_FUNCTIONS[report_type]
        results = func(from_date, to_date)

        col_info = REPORT_COLUMNS[report_type]
        headers = col_info["headers"]
        keys = col_info["keys"]

        # Configure treeview columns dynamically
        self.tree["columns"] = keys
        for key, header in zip(keys, headers):
            self.tree.heading(key, text=header)
            self.tree.column(key, width=120, anchor=tk.CENTER)

        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Build row tuples and populate treeview
        self._current_data = []
        for rec in results:
            row = tuple(rec.get(k) for k in keys)
            self._current_data.append(row)
            self.tree.insert("", tk.END, values=row)

        self._current_headers = headers
        self._current_title = f"{report_type} Report ({from_date} to {to_date})"

    def _on_export_pdf(self):
        """Export the current report to a PDF file."""
        if not self._current_data:
            messagebox.showwarning("Warning",
                                   "No data to export. Please generate a report first.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Save Report As",
        )
        if not filename:
            return  # user cancelled

        try:
            generate_pdf(self._current_title, self._current_headers,
                         self._current_data, filename)
            messagebox.showinfo("Success",
                                f"Report exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF:\n{e}")
