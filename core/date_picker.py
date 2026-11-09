"""
Custom DatePicker widget using only standard tkinter.
Works reliably on macOS (Tk 9.x), Windows, and Linux.
"""

import tkinter as tk
from tkinter import ttk
import calendar
from datetime import date


class DatePicker(ttk.Frame):
    """A date entry with a dropdown calendar button.

    Usage:
        dp = DatePicker(parent, textvariable=my_string_var)
        dp.pack()
        # my_string_var.get() returns 'YYYY-MM-DD'
    """

    def __init__(self, master, textvariable=None, width=12, **kwargs):
        super().__init__(master, **kwargs)

        self._var = textvariable or tk.StringVar()

        self._entry = ttk.Entry(self, textvariable=self._var, width=width)
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._btn = ttk.Button(self, text="\u25bc", width=2,
                               command=self._open_calendar)
        self._btn.pack(side=tk.LEFT, padx=(2, 0))

    def _open_calendar(self):
        """Open a calendar dialog to pick a date."""
        # Parse current value or default to today
        try:
            parts = self._var.get().strip().split("-")
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            current = date(y, m, d)
        except (ValueError, IndexError):
            current = date.today()

        dlg = _CalendarDialog(self.winfo_toplevel(), current)
        result = dlg.result
        if result is not None:
            self._var.set(result.strftime("%Y-%m-%d"))

    def get(self):
        return self._var.get()

    def set(self, value):
        self._var.set(value)


class _CalendarDialog(tk.Toplevel):
    """Modal calendar dialog for date selection."""

    DAYS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

    def __init__(self, parent, current_date):
        super().__init__(parent)
        self.result = None
        self._year = current_date.year
        self._month = current_date.month
        self._today = date.today()
        self._selected = current_date

        self.title("Select Date")
        self.resizable(False, False)
        self.configure(bg="white")

        # Centre on parent
        self.transient(parent)

        self._build_ui()
        self._render_month()

        # Make modal
        self.grab_set()
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.wait_window(self)

    def _build_ui(self):
        # Navigation header
        nav = tk.Frame(self, bg="#1a237e")
        nav.pack(fill=tk.X)

        btn_style = {"bg": "#1a237e", "fg": "white", "relief": "flat",
                     "font": ("Segoe UI", 12, "bold"), "cursor": "hand2",
                     "activebackground": "#534bae", "activeforeground": "white"}

        tk.Button(nav, text="\u25c0", command=self._prev_month,
                  **btn_style).pack(side=tk.LEFT, padx=5, pady=6)

        self._header_var = tk.StringVar()
        tk.Label(nav, textvariable=self._header_var, bg="#1a237e", fg="white",
                 font=("Segoe UI", 12, "bold"), width=18).pack(
            side=tk.LEFT, expand=True)

        tk.Button(nav, text="\u25b6", command=self._next_month,
                  **btn_style).pack(side=tk.RIGHT, padx=5, pady=6)

        # Day-of-week headers
        dow_frame = tk.Frame(self, bg="white")
        dow_frame.pack(fill=tk.X, padx=4, pady=(6, 0))
        for day in self.DAYS:
            tk.Label(dow_frame, text=day, width=4, bg="white", fg="#757575",
                     font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=1)

        # Calendar grid
        self._grid_frame = tk.Frame(self, bg="white")
        self._grid_frame.pack(fill=tk.BOTH, padx=4, pady=4)

        # Bottom buttons
        bottom = tk.Frame(self, bg="white")
        bottom.pack(fill=tk.X, padx=8, pady=(0, 8))

        tk.Button(bottom, text="Today", command=self._go_today,
                  bg="#e8eaf6", fg="#1a237e", relief="flat",
                  font=("Segoe UI", 10), cursor="hand2",
                  activebackground="#c5cae9", padx=10, pady=3).pack(
            side=tk.LEFT, padx=(0, 5))

        tk.Button(bottom, text="Cancel", command=self._cancel,
                  bg="#f5f5f5", fg="#546e7a", relief="flat",
                  font=("Segoe UI", 10), cursor="hand2",
                  activebackground="#e0e0e0", padx=10, pady=3).pack(
            side=tk.RIGHT)

    def _render_month(self):
        for w in self._grid_frame.winfo_children():
            w.destroy()

        self._header_var.set(f"{calendar.month_name[self._month]} {self._year}")

        cal = calendar.monthcalendar(self._year, self._month)
        for week in cal:
            row = tk.Frame(self._grid_frame, bg="white")
            row.pack(fill=tk.X)
            for day_num in week:
                if day_num == 0:
                    tk.Label(row, text="", width=4, bg="white").pack(
                        side=tk.LEFT, padx=1, pady=1)
                else:
                    d = date(self._year, self._month, day_num)
                    bg = "white"
                    fg = "#212121"

                    if d == self._today:
                        bg = "#e8eaf6"
                        fg = "#1a237e"
                    if d == self._selected:
                        bg = "#1565c0"
                        fg = "white"

                    lbl = tk.Label(
                        row, text=str(day_num), width=4, bg=bg, fg=fg,
                        font=("Segoe UI", 11), cursor="hand2", relief="flat")
                    lbl.pack(side=tk.LEFT, padx=1, pady=1)
                    lbl.bind("<Button-1>",
                             lambda e, dn=day_num: self._pick(dn))
                    lbl.bind("<Enter>",
                             lambda e, w=lbl: w.configure(bg="#bbdefb")
                             if w.cget("bg") != "#1565c0" else None)
                    lbl.bind("<Leave>",
                             lambda e, w=lbl, d=d: w.configure(
                                 bg="#e8eaf6" if d == self._today else
                                 "#1565c0" if d == self._selected else "white"))

    def _pick(self, day_num):
        self.result = date(self._year, self._month, day_num)
        self.destroy()

    def _prev_month(self):
        if self._month == 1:
            self._month = 12
            self._year -= 1
        else:
            self._month -= 1
        self._render_month()

    def _next_month(self):
        if self._month == 12:
            self._month = 1
            self._year += 1
        else:
            self._month += 1
        self._render_month()

    def _go_today(self):
        self.result = self._today
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()
