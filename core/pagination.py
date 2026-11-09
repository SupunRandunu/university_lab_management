"""
Reusable pagination bar for Treeview tables.
"""

import tkinter as tk
from tkinter import ttk


PAGE_SIZE = 15


class PaginationBar(ttk.Frame):
    """A pagination control bar that manages paging for a Treeview.

    Usage:
        bar = PaginationBar(parent, tree=my_treeview, page_size=15)
        bar.pack(fill=tk.X)
        bar.set_data(all_rows)   # list of tuples/values
        # Treeview is populated with page 1 automatically.
    """

    def __init__(self, master, tree, page_size=PAGE_SIZE, tags_list=None, **kwargs):
        super().__init__(master, **kwargs)
        self._tree = tree
        self._page_size = page_size
        self._data = []          # list of row value tuples
        self._tags = []          # optional parallel list of tag tuples
        self._current_page = 1
        self._total_pages = 1

        self._build_ui()

    def _build_ui(self):
        # Left: record count
        self._count_var = tk.StringVar(value="0 records")
        ttk.Label(self, textvariable=self._count_var).pack(side=tk.LEFT, padx=5)

        # Right: page controls
        nav = ttk.Frame(self)
        nav.pack(side=tk.RIGHT)

        self._prev_btn = ttk.Button(nav, text="Previous",
                                     command=self._prev_page, width=10)
        self._prev_btn.pack(side=tk.LEFT, padx=2)

        self._page_var = tk.StringVar(value="Page 1 / 1")
        ttk.Label(nav, textvariable=self._page_var, width=14,
                  anchor=tk.CENTER).pack(side=tk.LEFT, padx=5)

        self._next_btn = ttk.Button(nav, text="Next",
                                     command=self._next_page, width=10)
        self._next_btn.pack(side=tk.LEFT, padx=2)

    def set_data(self, rows, tags_list=None):
        """Set the full data and display page 1.

        Args:
            rows: list of tuples — each tuple is one row of treeview values.
            tags_list: optional parallel list of tag tuples for each row.
        """
        self._data = list(rows)
        self._tags = list(tags_list) if tags_list else []
        total = len(self._data)
        self._total_pages = max(1, (total + self._page_size - 1) // self._page_size)
        self._current_page = 1
        self._count_var.set(f"{total} record(s)")
        self._render_page()

    def _render_page(self):
        """Clear the tree and populate it with the current page's rows."""
        for item in self._tree.get_children():
            self._tree.delete(item)

        start = (self._current_page - 1) * self._page_size
        end = start + self._page_size
        page_rows = self._data[start:end]
        page_tags = self._tags[start:end] if self._tags else []

        for i, row in enumerate(page_rows):
            kw = {}
            if page_tags and i < len(page_tags):
                kw["tags"] = page_tags[i]
            self._tree.insert("", tk.END, values=row, **kw)

        self._page_var.set(f"Page {self._current_page} / {self._total_pages}")
        self._prev_btn.state(["disabled"] if self._current_page <= 1 else ["!disabled"])
        self._next_btn.state(["disabled"] if self._current_page >= self._total_pages else ["!disabled"])

    def _prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self._render_page()

    def _next_page(self):
        if self._current_page < self._total_pages:
            self._current_page += 1
            self._render_page()
