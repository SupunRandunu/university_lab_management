"""
Custom TimePicker widget using only standard tkinter.
Provides hour and minute spinboxes for easy time selection.
"""

import tkinter as tk
from tkinter import ttk


class TimePicker(ttk.Frame):
    """A time picker with hour and minute spinboxes.

    Usage:
        tp = TimePicker(parent, textvariable=my_string_var)
        tp.pack()
        # my_string_var.get() returns 'HH:MM'
    """

    def __init__(self, master, textvariable=None, **kwargs):
        super().__init__(master, **kwargs)

        self._var = textvariable or tk.StringVar()

        # Parse initial value
        hour, minute = self._parse_time(self._var.get())

        self._hour_var = tk.StringVar(value=f"{hour:02d}")
        self._min_var = tk.StringVar(value=f"{minute:02d}")

        # Hour spinbox
        self._hour_spin = tk.Spinbox(
            self, from_=0, to=23, width=3, format="%02.0f",
            textvariable=self._hour_var, wrap=True,
            font=("Segoe UI", 11), justify=tk.CENTER,
            command=self._update_var)
        self._hour_spin.pack(side=tk.LEFT)

        # Colon separator
        tk.Label(self, text=":", font=("Segoe UI", 12, "bold"),
                 background=self._get_bg()).pack(side=tk.LEFT, padx=1)

        # Minute spinbox
        self._min_spin = tk.Spinbox(
            self, from_=0, to=59, width=3, format="%02.0f",
            textvariable=self._min_var, wrap=True,
            font=("Segoe UI", 11), justify=tk.CENTER,
            increment=5, command=self._update_var)
        self._min_spin.pack(side=tk.LEFT)

        # Bind key release to sync
        self._hour_spin.bind("<KeyRelease>", lambda _e: self._update_var())
        self._min_spin.bind("<KeyRelease>", lambda _e: self._update_var())

        # Sync initial value
        self._update_var()

        # Watch external changes to the variable
        self._var.trace_add("write", self._on_var_changed)

    def _get_bg(self):
        """Get the background colour from the parent style."""
        try:
            return self.cget("background")
        except tk.TclError:
            return "#f5f5f5"

    def _parse_time(self, time_str):
        """Parse 'HH:MM' string. Returns (hour, minute) defaulting to (8, 0)."""
        try:
            parts = time_str.strip().split(":")
            h = max(0, min(23, int(parts[0])))
            m = max(0, min(59, int(parts[1])))
            return h, m
        except (ValueError, IndexError):
            return 8, 0

    def _update_var(self):
        """Sync the spinbox values into the textvariable."""
        try:
            h = max(0, min(23, int(self._hour_var.get())))
            m = max(0, min(59, int(self._min_var.get())))
        except ValueError:
            return
        self._hour_var.set(f"{h:02d}")
        self._min_var.set(f"{m:02d}")
        new_val = f"{h:02d}:{m:02d}"
        if self._var.get() != new_val:
            self._var.set(new_val)

    def _on_var_changed(self, *_args):
        """React to external changes to the textvariable."""
        h, m = self._parse_time(self._var.get())
        if self._hour_var.get() != f"{h:02d}":
            self._hour_var.set(f"{h:02d}")
        if self._min_var.get() != f"{m:02d}":
            self._min_var.set(f"{m:02d}")

    def get(self):
        return self._var.get()

    def set(self, value):
        self._var.set(value)
