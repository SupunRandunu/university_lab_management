import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from core.date_picker import DatePicker

from bundles.maintenance.models import (
    report_maintenance,
    complete_maintenance,
    get_pending_maintenance,
)
from bundles.equipment.models import get_all_equipment
from core.validators import validate_not_empty, validate_date_format


class MaintenanceFrame(ttk.Frame):
    """Interface for reporting damaged equipment and completing repairs (staff only).

    Fix #4: report and complete are separate operations.
    """

    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self._selected_maintenance_id = None

        self._build_top_row()
        self._build_treeview()
        self._refresh_equipment()
        self._refresh_table()

        self.bind("<Visibility>", lambda _e: self._on_tab_visible())

    def _on_tab_visible(self):
        self._refresh_equipment()
        self._refresh_table()

    # ----- UI Construction ------------------------------------------------

    def _build_top_row(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=(10, 5))

        # --- Left: Report Damaged Equipment ---
        report_frame = ttk.LabelFrame(top, text="Report Damaged Equipment",
                                      padding=10)
        report_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(report_frame, text="Equipment:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.equip_var = tk.StringVar()
        self.equip_combo = ttk.Combobox(report_frame, textvariable=self.equip_var,
                                        state="readonly", width=30)
        self.equip_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(report_frame, text="Problem Description:").grid(
            row=1, column=0, sticky=tk.NW, padx=5, pady=4)
        self.desc_text = tk.Text(report_frame, width=30, height=4)
        self.desc_text.grid(row=1, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Button(report_frame, text="Report Damage",
                   command=self._on_report, style="Orange.TButton").grid(
            row=2, column=0, columnspan=2, pady=(5, 0))

        # --- Right: Complete Repair ---
        complete_frame = ttk.LabelFrame(top, text="Complete Repair",
                                        padding=10)
        complete_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Label(complete_frame,
                  text="Select a record from the table below",
                  foreground="grey").grid(
            row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=4)

        ttk.Label(complete_frame, text="Completion Date:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=4)
        self.comp_date_var = tk.StringVar(value=date.today().isoformat())
        DatePicker(complete_frame, textvariable=self.comp_date_var,
                   width=15).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(complete_frame, text="Remarks:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=4)
        self.remarks_var = tk.StringVar()
        ttk.Entry(complete_frame, textvariable=self.remarks_var,
                  width=30).grid(row=2, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Button(complete_frame, text="Mark as Completed",
                   command=self._on_complete, style="Green.TButton").grid(
            row=3, column=0, columnspan=2, pady=(5, 0))

    def _build_treeview(self):
        tree_label = ttk.LabelFrame(self, text="Under Maintenance", padding=5)
        tree_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        columns = ("MaintenanceID", "EquipmentName",
                   "Issue", "ReportedBy", "ReportedDate", "Status")
        self.tree = ttk.Treeview(tree_label, columns=columns,
                                 show="headings", selectmode="browse")

        self.tree.heading("MaintenanceID", text="Maintenance ID")
        self.tree.heading("EquipmentName", text="Equipment Name")
        self.tree.heading("Issue", text="Issue")
        self.tree.heading("ReportedBy", text="Reported By")
        self.tree.heading("ReportedDate", text="Reported Date")
        self.tree.heading("Status", text="Status")

        self.tree.column("MaintenanceID", width=100, anchor=tk.CENTER)
        self.tree.column("EquipmentName", width=160)
        self.tree.column("Issue", width=180)
        self.tree.column("ReportedBy", width=120)
        self.tree.column("ReportedDate", width=110, anchor=tk.CENTER)
        self.tree.column("Status", width=130, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_label, orient=tk.VERTICAL,
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

    # ----- Data helpers ---------------------------------------------------

    def _refresh_equipment(self):
        """Populate the equipment combobox excluding items already under maintenance."""
        all_eq = get_all_equipment()
        available = [eq for eq in all_eq
                     if eq["Status"] != "Under Maintenance"]
        self._equip_list = available
        self._equip_map = {}
        display_values = []
        for eq in available:
            display = eq["Name"]
            display_values.append(display)
            self._equip_map[display] = eq["EquipmentID"]
        self.equip_combo["values"] = display_values

    def _refresh_table(self):
        """Reload pending maintenance records into the treeview."""
        self._maintenance_ids = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        for rec in get_pending_maintenance():
            self._maintenance_ids.append(rec["MaintenanceID"])
            self.tree.insert("", tk.END, values=(
                rec["MaintenanceID"][:8] + "...",
                rec["EquipmentName"],
                rec["IssueDescription"],
                rec["ReportedByName"],
                rec["ReportedDate"],
                rec["Status"],
            ))
        self._selected_maintenance_id = None

    # ----- Event handlers -------------------------------------------------

    def _on_row_select(self, _event=None):
        """Store the selected maintenance record ID for completion."""
        selected = self.tree.selection()
        if not selected:
            return
        idx = self.tree.index(selected[0])
        if idx < len(self._maintenance_ids):
            self._selected_maintenance_id = self._maintenance_ids[idx]

    def _on_report(self):
        """Report a new maintenance issue."""
        equip_str = self.equip_var.get()
        if not equip_str:
            messagebox.showerror("Validation Error",
                                 "Please select an equipment item.")
            return

        description = self.desc_text.get("1.0", tk.END).strip()
        ok, msg = validate_not_empty(description, "Problem Description")
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return

        # Look up equipment UUID from display name
        equipment_id = self._equip_map.get(equip_str)
        if not equipment_id:
            messagebox.showerror("Validation Error",
                                 "Could not find the selected equipment.")
            return

        reported_date = date.today().isoformat()

        success, result_msg = report_maintenance(
            equipment_id,
            self.current_user["UserID"],
            description,
            reported_date,
        )
        if success:
            messagebox.showinfo("Success", result_msg)
            self.equip_var.set("")
            self.desc_text.delete("1.0", tk.END)
            self._refresh_equipment()
            self._refresh_table()
        else:
            messagebox.showerror("Error", result_msg)

    def _on_complete(self):
        """Mark the selected maintenance record as completed."""
        if self._selected_maintenance_id is None:
            messagebox.showwarning("Warning",
                                   "Please select a maintenance record from the table.")
            return

        comp_date = self.comp_date_var.get().strip()
        ok, msg = validate_date_format(comp_date)
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return

        remarks = self.remarks_var.get().strip()

        success, result_msg = complete_maintenance(
            self._selected_maintenance_id,
            comp_date,
            remarks,
        )
        if success:
            messagebox.showinfo("Success", result_msg)
            self.comp_date_var.set(date.today().isoformat())
            self.remarks_var.set("")
            self._refresh_equipment()
            self._refresh_table()
        else:
            messagebox.showerror("Error", result_msg)
