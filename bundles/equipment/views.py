import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from core.date_picker import DatePicker

from bundles.equipment.models import (
    get_all_laboratories,
    get_category_names,
    get_all_categories,
    add_category,
    update_category,
    delete_category,
    add_equipment,
    update_equipment,
    delete_equipment,
    get_all_equipment,
    search_equipment,
)
from core.validators import (
    validate_not_empty,
    validate_date_format,
)

STATUS_OPTIONS = ("Available", "Borrowed", "Under Maintenance")


# ---------------------------------------------------------------------------
# FR02 - Equipment Management (Staff only)
# ---------------------------------------------------------------------------

class EquipmentManagementFrame(ttk.Frame):
    """CRUD interface for managing laboratory equipment (staff only).

    EquipmentID is now a UUID generated automatically -- there is no
    user-editable ID field.  The full UUID of the currently selected row
    is stored in ``self._selected_uuid``.
    """

    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self._editing = False          # True when a row is selected for editing
        self._selected_uuid = None     # full UUID of the selected equipment

        # --- Laboratory lookup (id -> name and name -> id) ----------------
        self._labs = []                # list of lab dicts
        self._lab_names = []           # display strings "LabName"
        self._lab_id_map = {}          # lab_name -> LabID (UUID)

        self._build_form()
        self._build_treeview()
        self._load_laboratories()
        self._load_categories()
        self._refresh_table()

        # Refresh table when this tab becomes visible
        self.bind("<Visibility>", lambda _e: self._refresh_table())

    # ----- UI Construction ------------------------------------------------

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Equipment Details", padding=10)
        form.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Row 0
        ttk.Label(form, text="Name:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=30).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(form, text="Category:").grid(
            row=0, column=2, sticky=tk.W, padx=5, pady=4)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            form, textvariable=self.category_var,
            state="readonly", width=23)
        self.category_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=4)
        self.category_combo.bind("<ButtonPress>", lambda _e: self._load_categories())

        # Row 1
        ttk.Label(form, text="Laboratory:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=4)
        self.lab_var = tk.StringVar()
        self.lab_combo = ttk.Combobox(form, textvariable=self.lab_var,
                                      state="readonly", width=25)
        self.lab_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(form, text="Purchase Date:").grid(
            row=1, column=2, sticky=tk.W, padx=5, pady=4)
        self.date_var = tk.StringVar()
        self.date_entry = DatePicker(form, textvariable=self.date_var, width=15)
        self.date_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=4)

        # Row 2
        ttk.Label(form, text="Status:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=4)
        self.status_var = tk.StringVar(value=STATUS_OPTIONS[0])
        self.status_combo = ttk.Combobox(
            form, textvariable=self.status_var, values=STATUS_OPTIONS,
            state="disabled", width=20)
        self.status_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=4)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(btn_frame, text="Add",
                   command=self._on_add, style="Green.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update",
                   command=self._on_update, style="Blue.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete",
                   command=self._on_delete, style="Red.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear",
                   command=self._clear_form, style="Grey.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh",
                   command=self._refresh_table, style="Blue.TButton").pack(side=tk.LEFT, padx=5)

    def _build_treeview(self):
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 0))

        columns = ("EquipmentID", "Name", "Category",
                   "Laboratory", "PurchaseDate", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=columns,
                                 show="headings", selectmode="browse")

        self.tree.heading("EquipmentID", text="Equipment ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Laboratory", text="Laboratory")
        self.tree.heading("PurchaseDate", text="Purchase Date")
        self.tree.heading("Status", text="Status")

        self.tree.column("EquipmentID", width=100, anchor=tk.CENTER)
        self.tree.column("Name", width=180)
        self.tree.column("Category", width=140)
        self.tree.column("Laboratory", width=140)
        self.tree.column("PurchaseDate", width=110, anchor=tk.CENTER)
        self.tree.column("Status", width=130, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

    # ----- Data helpers ---------------------------------------------------

    def _load_laboratories(self):
        """Populate the laboratory combobox."""
        self._labs = get_all_laboratories()
        self._lab_names = [lab["LabName"] for lab in self._labs]
        self._lab_id_map = {lab["LabName"]: lab["LabID"]
                           for lab in self._labs}
        self.lab_combo["values"] = self._lab_names

    def _load_categories(self):
        """Populate the category combobox from the database."""
        self.category_combo["values"] = get_category_names()

    def _refresh_table(self):
        """Reload all equipment into the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for eq in get_all_equipment():
            full_uuid = eq["EquipmentID"]
            self.tree.insert("", tk.END, values=(
                full_uuid[:8],
                eq["Name"],
                eq["Category"],
                eq.get("LabName", ""),
                eq["PurchaseDate"],
                eq["Status"],
            ), tags=(full_uuid,))

    # ----- Validation -----------------------------------------------------

    def _validate_fields(self):
        """Validate all form fields.

        Returns (True, "") on success or (False, error_message).
        """
        ok, msg = validate_not_empty(self.name_var.get(), "Name")
        if not ok:
            return False, msg

        ok, msg = validate_not_empty(self.category_var.get(), "Category")
        if not ok:
            return False, msg

        if not self.lab_var.get():
            return False, "Please select a Laboratory."

        ok, msg = validate_date_format(self.date_var.get())
        if not ok:
            return False, msg

        if not self.status_var.get():
            return False, "Please select a Status."

        return True, ""

    # ----- Event handlers -------------------------------------------------

    def _on_row_select(self, _event=None):
        """Populate form from the selected treeview row."""
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        values = self.tree.item(item_id, "values")
        tags = self.tree.item(item_id, "tags")

        # Store the full UUID from the tag
        self._selected_uuid = tags[0] if tags else None

        self.name_var.set(values[1])
        self.category_var.set(values[2])
        self.lab_var.set(values[3])
        self.date_var.set(values[4])
        self.status_var.set(values[5])
        self.status_combo.configure(state="readonly")

        self._editing = True

    def _clear_form(self):
        """Reset all form fields."""
        self.name_var.set("")
        self.category_var.set("")
        self.lab_var.set("")
        self.date_var.set(date.today().strftime("%Y-%m-%d"))
        self.status_combo.configure(state="readonly")
        self.status_var.set(STATUS_OPTIONS[0])
        self.status_combo.configure(state="disabled")
        self._editing = False
        self._selected_uuid = None
        # Deselect treeview
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)

    def _on_add(self):
        """Add a new equipment record (UUID is auto-generated)."""
        ok, msg = self._validate_fields()
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return

        lab_id = self._lab_id_map.get(self.lab_var.get())
        success, result_msg = add_equipment(
            self.name_var.get().strip(),
            self.category_var.get().strip(),
            lab_id,
            self.date_var.get().strip(),
            self.status_var.get(),
        )
        if success:
            messagebox.showinfo("Success", result_msg)
            self._clear_form()
            self._refresh_table()
        else:
            messagebox.showerror("Error", result_msg)

    def _on_update(self):
        """Update the selected equipment record."""
        if not self._editing or not self._selected_uuid:
            messagebox.showwarning("Warning",
                                   "Please select an equipment to update.")
            return

        ok, msg = self._validate_fields()
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return

        lab_id = self._lab_id_map.get(self.lab_var.get())
        success, result_msg = update_equipment(
            self._selected_uuid,
            self.name_var.get().strip(),
            self.category_var.get().strip(),
            lab_id,
            self.date_var.get().strip(),
            self.status_var.get(),
        )
        if success:
            messagebox.showinfo("Success", result_msg)
            self._clear_form()
            self._refresh_table()
        else:
            messagebox.showerror("Error", result_msg)

    def _on_delete(self):
        """Delete the selected equipment record after confirmation."""
        if not self._editing or not self._selected_uuid:
            messagebox.showwarning("Warning",
                                   "Please select an equipment to delete.")
            return

        eq_name = self.name_var.get().strip()
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete equipment '{eq_name}'?"
        ):
            return

        success, result_msg = delete_equipment(self._selected_uuid)
        if success:
            messagebox.showinfo("Success", result_msg)
            self._clear_form()
            self._refresh_table()
        else:
            messagebox.showerror("Error", result_msg)


# ---------------------------------------------------------------------------
# FR03 - Equipment Search (Both roles)
# ---------------------------------------------------------------------------

class EquipmentSearchFrame(ttk.Frame):
    """Search interface for equipment (available to both staff and students)."""

    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user

        self._build_search_bar()
        self._build_treeview()
        self._show_all()

        self.bind("<Visibility>", lambda _e: self._show_all())

    # ----- UI Construction ------------------------------------------------

    def _build_search_bar(self):
        bar = ttk.Frame(self, padding=(10, 10, 10, 5))
        bar.pack(fill=tk.X)

        ttk.Label(bar, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(bar, textvariable=self.search_var,
                                      width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda _e: self._on_search())

        ttk.Button(bar, text="Search",
                   command=self._on_search, style="Blue.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(bar, text="Show All",
                   command=self._show_all, style="Grey.TButton").pack(side=tk.LEFT, padx=5)

    def _build_treeview(self):
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        columns = ("EquipmentID", "Name", "Category",
                   "Laboratory", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=columns,
                                 show="headings", selectmode="browse")

        self.tree.heading("EquipmentID", text="Equipment ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Laboratory", text="Laboratory")
        self.tree.heading("Status", text="Status")

        self.tree.column("EquipmentID", width=100, anchor=tk.CENTER)
        self.tree.column("Name", width=200)
        self.tree.column("Category", width=160)
        self.tree.column("Laboratory", width=160)
        self.tree.column("Status", width=130, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ----- Actions --------------------------------------------------------

    def _populate_tree(self, equipment_list):
        """Clear and repopulate the treeview with the given list."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for eq in equipment_list:
            self.tree.insert("", tk.END, values=(
                eq["EquipmentID"][:8],
                eq["Name"],
                eq["Category"],
                eq.get("LabName", ""),
                eq["Status"],
            ))

    def _on_search(self):
        """Search equipment by the text entered."""
        text = self.search_var.get().strip()
        if not text:
            messagebox.showwarning("Warning",
                                   "Please enter a search term.")
            return
        results = search_equipment(text)
        if not results:
            messagebox.showinfo("No Results", "No equipment found.")
        self._populate_tree(results)

    def _show_all(self):
        """Display all equipment in the treeview."""
        self.search_var.set("")
        results = get_all_equipment()
        self._populate_tree(results)


# ---------------------------------------------------------------------------
# Category Management (Admin only)
# ---------------------------------------------------------------------------

class CategoryManagementFrame(ttk.Frame):
    """Admin-only frame for managing equipment categories."""

    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self._selected_cat_id = None

        self._build_form()
        self._build_treeview()
        self._load_categories()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Category Details", padding=10)
        form.pack(fill=tk.X, padx=10, pady=(10, 5))

        ttk.Label(form, text="Category Name:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=30).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(form, text="Description:").grid(
            row=0, column=2, sticky=tk.W, padx=5, pady=4)
        self.desc_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.desc_var, width=50).grid(
            row=0, column=3, sticky=tk.EW, padx=5, pady=4)

        form.columnconfigure(3, weight=1)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=1, column=0, columnspan=4, pady=(10, 0))

        ttk.Button(btn_frame, text="Add Category",
                   command=self._on_add, style="Green.TButton").pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update",
                   command=self._on_update, style="Blue.TButton").pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete",
                   command=self._on_delete, style="Red.TButton").pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear",
                   command=self._clear_form, style="Grey.TButton").pack(
            side=tk.LEFT, padx=5)

    def _build_treeview(self):
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        columns = ("CategoryID", "CategoryName", "Description")
        self.tree = ttk.Treeview(tree_frame, columns=columns,
                                 show="headings", selectmode="browse")

        self.tree.heading("CategoryID", text="ID")
        self.tree.heading("CategoryName", text="Category Name")
        self.tree.heading("Description", text="Description")

        self.tree.column("CategoryID", width=80, anchor=tk.CENTER)
        self.tree.column("CategoryName", width=200)
        self.tree.column("Description", width=400)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

    def _load_categories(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for cat in get_all_categories():
            self.tree.insert("", tk.END, values=(
                cat["CategoryID"][:8],
                cat["CategoryName"],
                cat.get("Description") or "",
            ), tags=(cat["CategoryID"],))

    def _on_row_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        tags = self.tree.item(selected[0], "tags")
        self._selected_cat_id = tags[0] if tags else None
        self.name_var.set(values[1])
        self.desc_var.set(values[2])

    def _clear_form(self):
        self._selected_cat_id = None
        self.name_var.set("")
        self.desc_var.set("")
        self.tree.selection_remove(*self.tree.selection())

    def _on_add(self):
        name = self.name_var.get().strip()
        ok, msg = validate_not_empty(name, "Category Name")
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return
        success, msg = add_category(name, self.desc_var.get().strip())
        if success:
            messagebox.showinfo("Success", msg)
            self._clear_form()
            self._load_categories()
        else:
            messagebox.showerror("Error", msg)

    def _on_update(self):
        if self._selected_cat_id is None:
            messagebox.showerror("Error", "Please select a category to update.")
            return
        name = self.name_var.get().strip()
        ok, msg = validate_not_empty(name, "Category Name")
        if not ok:
            messagebox.showerror("Validation Error", msg)
            return
        success, msg = update_category(
            self._selected_cat_id, name, self.desc_var.get().strip())
        if success:
            messagebox.showinfo("Success", msg)
            self._clear_form()
            self._load_categories()
        else:
            messagebox.showerror("Error", msg)

    def _on_delete(self):
        if self._selected_cat_id is None:
            messagebox.showerror("Error", "Please select a category to delete.")
            return
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete category '{self.name_var.get()}'?"
        ):
            return
        success, msg = delete_category(self._selected_cat_id)
        if success:
            messagebox.showinfo("Success", msg)
            self._clear_form()
            self._load_categories()
        else:
            messagebox.showerror("Error", msg)
