"""
Application theme - colours and styling for the University Lab Management System.
Uses Material Design colour palette for consistency.
"""

# ── Brand colours ──────────────────────────────────────────
PRIMARY = "#1a237e"        # Dark indigo  (header, logo)
PRIMARY_LIGHT = "#534bae"
PRIMARY_DARK = "#000051"
ACCENT = "#0288d1"         # Light blue   (highlights)
ACCENT_LIGHT = "#5eb8ff"
WHITE = "#ffffff"
BG_LIGHT = "#f5f5f5"       # Light grey background
TEXT_DARK = "#212121"
TEXT_LIGHT = "#757575"
BORDER = "#bdbdbd"

# ── Button colours (Material Design) ──────────────────────
BTN_GREEN = "#2e7d32"       # Green 800   – positive actions (Add, Approve, Submit, Issue)
BTN_GREEN_HOVER = "#43a047" # Green 600   – brighter on hover
BTN_RED = "#c62828"         # Red 800     – destructive actions (Delete, Reject, Logout)
BTN_RED_HOVER = "#e53935"   # Red 600     – brighter on hover
BTN_BLUE = "#1565c0"        # Blue 800    – neutral actions (Search, Generate, Refresh, Update)
BTN_BLUE_HOVER = "#1e88e5"  # Blue 600    – brighter on hover
BTN_ORANGE = "#e65100"      # Orange 900  – warning actions (Reset Password, Report Damage)
BTN_ORANGE_HOVER = "#fb8c00" # Orange 600  – brighter on hover
BTN_GREY = "#546e7a"        # Blue Grey 600 – passive actions (Clear, Show All, Cancel)
BTN_GREY_HOVER = "#78909c"  # Blue Grey 400 – brighter on hover

# ── Table colours ─────────────────────────────────────────
TABLE_HEADER_BG = "#1a237e"     # Dark indigo header
TABLE_HEADER_FG = "#ffffff"     # White text on header
TABLE_ROW_BG = "#ffffff"        # White rows
TABLE_ROW_ALT = "#e8eaf6"      # Very light indigo alternate rows
TABLE_SELECT_BG = "#1565c0"     # Blue selection
TABLE_SELECT_FG = "#ffffff"
TABLE_BORDER = "#c5cae9"        # Light indigo border

# ── Tab colours ───────────────────────────────────────────
TAB_SELECTED_BG = "#ffffff"
TAB_SELECTED_FG = "#1a237e"
TAB_BG = "#c5cae9"              # Light indigo
TAB_FG = "#1a237e"


def apply_theme(root):
    """Apply the complete colour theme to the application."""
    from tkinter import ttk
    s = ttk.Style(root)

    # Use 'clam' theme — the default 'aqua' theme on macOS ignores
    # custom button background colours entirely.
    s.theme_use("clam")

    # ── General ────────────────────────────────────────────
    s.configure(".", font=("Segoe UI", 10), background=BG_LIGHT)
    s.configure("TFrame", background=BG_LIGHT)
    s.configure("TLabel", background=BG_LIGHT, foreground=TEXT_DARK)
    s.configure("TLabelframe", background=BG_LIGHT, foreground=PRIMARY)
    s.configure("TLabelframe.Label", background=BG_LIGHT, foreground=PRIMARY,
                font=("Segoe UI", 10, "bold"))

    # ── Default Button ─────────────────────────────────────
    s.configure("TButton", padding=(14, 6), font=("Segoe UI", 10),
                background=BG_LIGHT, foreground=TEXT_DARK)
    s.map("TButton",
          background=[("active", BORDER), ("pressed", BORDER)])

    # ── Coloured Button Styles ─────────────────────────────
    # Green buttons – Add, Approve, Submit, Issue, Save
    s.configure("Green.TButton", background=BTN_GREEN, foreground=WHITE,
                padding=(14, 6), font=("Segoe UI", 10, "bold"),
                borderwidth=0)
    s.map("Green.TButton",
          background=[("active", BTN_GREEN_HOVER), ("pressed", BTN_GREEN)],
          foreground=[("active", WHITE), ("pressed", WHITE)])

    # Red buttons – Delete, Reject, Logout
    s.configure("Red.TButton", background=BTN_RED, foreground=WHITE,
                padding=(14, 6), font=("Segoe UI", 10, "bold"),
                borderwidth=0)
    s.map("Red.TButton",
          background=[("active", BTN_RED_HOVER), ("pressed", BTN_RED)],
          foreground=[("active", WHITE), ("pressed", WHITE)])

    # Blue buttons – Search, Generate, Refresh, Update, View
    s.configure("Blue.TButton", background=BTN_BLUE, foreground=WHITE,
                padding=(14, 6), font=("Segoe UI", 10, "bold"),
                borderwidth=0)
    s.map("Blue.TButton",
          background=[("active", BTN_BLUE_HOVER), ("pressed", BTN_BLUE)],
          foreground=[("active", WHITE), ("pressed", WHITE)])

    # Orange buttons – Reset Password, Report Damage, Return, Complete
    s.configure("Orange.TButton", background=BTN_ORANGE, foreground=WHITE,
                padding=(14, 6), font=("Segoe UI", 10, "bold"),
                borderwidth=0)
    s.map("Orange.TButton",
          background=[("active", BTN_ORANGE_HOVER), ("pressed", BTN_ORANGE)],
          foreground=[("active", WHITE), ("pressed", WHITE)])

    # Grey buttons – Clear, Show All, Cancel
    s.configure("Grey.TButton", background=BTN_GREY, foreground=WHITE,
                padding=(14, 6), font=("Segoe UI", 10),
                borderwidth=0)
    s.map("Grey.TButton",
          background=[("active", BTN_GREY_HOVER), ("pressed", BTN_GREY)],
          foreground=[("active", WHITE), ("pressed", WHITE)])

    # ── Notebook Tabs ──────────────────────────────────────
    s.configure("TNotebook", background=BG_LIGHT)
    s.configure("TNotebook.Tab", padding=(14, 6), font=("Segoe UI", 10))
    s.map("TNotebook.Tab",
          background=[("selected", TAB_SELECTED_BG), ("!selected", TAB_BG)],
          foreground=[("selected", TAB_SELECTED_FG), ("!selected", TAB_FG)])

    # ── Treeview (Tables) ─────────────────────────────────
    s.configure("Treeview",
                background=TABLE_ROW_BG,
                foreground=TEXT_DARK,
                fieldbackground=TABLE_ROW_BG,
                rowheight=28,
                font=("Segoe UI", 10))
    s.configure("Treeview.Heading",
                background=TABLE_HEADER_BG,
                foreground=TABLE_HEADER_FG,
                font=("Segoe UI", 10, "bold"),
                padding=(5, 5))
    s.map("Treeview.Heading",
          background=[("active", PRIMARY_LIGHT)])
    s.map("Treeview",
          background=[("selected", TABLE_SELECT_BG)],
          foreground=[("selected", TABLE_SELECT_FG)])

    # ── Entry / Combobox ───────────────────────────────────
    s.configure("TEntry", padding=(6, 4))
    s.configure("TCombobox", padding=(6, 4))

    root.configure(bg=BG_LIGHT)


def draw_logo(canvas, cx, cy, size=60):
    """Draw a microscope logo on a tkinter Canvas centred at (cx, cy)."""
    r = size // 2

    # Outer circle
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                       fill=PRIMARY, outline=PRIMARY_DARK, width=2)

    # Microscope eyepiece (top)
    ew = size * 0.08
    canvas.create_rectangle(cx - ew, cy - r * 0.75, cx + ew, cy - r * 0.55,
                            fill=WHITE, outline=WHITE)
    # Eyepiece cap
    canvas.create_rectangle(cx - ew * 1.6, cy - r * 0.78, cx + ew * 1.6, cy - r * 0.72,
                            fill=ACCENT, outline=ACCENT)

    # Body tube (angled)
    canvas.create_polygon(
        cx - ew, cy - r * 0.55,
        cx + ew, cy - r * 0.55,
        cx + ew + size * 0.05, cy + r * 0.15,
        cx - ew + size * 0.05, cy + r * 0.15,
        fill=WHITE, outline=WHITE)

    # Objective lens
    canvas.create_rectangle(
        cx - ew * 0.6 + size * 0.05, cy + r * 0.15,
        cx + ew * 1.2 + size * 0.05, cy + r * 0.28,
        fill=ACCENT, outline=ACCENT)

    # Stage (horizontal platform)
    canvas.create_rectangle(cx - r * 0.45, cy + r * 0.28,
                            cx + r * 0.45, cy + r * 0.35,
                            fill=WHITE, outline=WHITE)

    # Arm (vertical support)
    canvas.create_rectangle(cx - r * 0.08, cy - r * 0.3,
                            cx + r * 0.08, cy + r * 0.55,
                            fill=WHITE, outline=PRIMARY_DARK, width=1)

    # Base
    canvas.create_oval(cx - r * 0.4, cy + r * 0.48,
                       cx + r * 0.4, cy + r * 0.68,
                       fill=WHITE, outline=PRIMARY_DARK, width=1)

    # Label
    canvas.create_text(cx, cy + r * 0.85, text="LMS",
                       font=("Segoe UI", int(size * 0.13), "bold"), fill=WHITE)
