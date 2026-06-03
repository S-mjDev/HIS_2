from tkinter import *
from tkinter import ttk

# ============== THEME ==============
T = {
    "bg":        "#f0f4f8",
    "panel":     "#ffffff",
    "card":      "#ffffff",
    "sidebar":   "#1a2332",
    "sidebar2":  "#243447",
    "accent":    "#2563eb",
    "accent_h":  "#1d4ed8",
    "accent_lt": "#dbeafe",
    "text":      "#1e293b",
    "muted":     "#64748b",
    "border":    "#e2e8f0",
    "border2":   "#cbd5e1",
    "danger":    "#dc2626",
    "danger_lt": "#fee2e2",
    "warning":   "#d97706",
    "success":   "#059669",
    "success_lt": "#d1fae5",
    "white":     "#ffffff",
    "entry_bg":  "#f8fafc",
    "entry_fg":  "#1e293b",
    "row_even":  "#f8fafc",
    "row_odd":   "#ffffff",
    "row_alt":   "#f8fafc",
    "row_sel":   "#dbeafe",
    "heading_bg": "#f1f5f9",
}

FONT = {
    "h1":     ("Georgia", 18, "bold"),
    "h2":     ("Georgia", 14, "bold"),
    "h3":     ("Georgia", 11, "bold"),
    "body":   ("Calibri", 10),
    "body_b": ("Calibri", 10, "bold"),
    "small":  ("Calibri", 9),
    "label":  ("Calibri", 9, "bold"),
    "mono":   ("Consolas", 11, "bold"),
    "nav":    ("Calibri", 10, "bold"),
    "tag":    ("Calibri", 8, "bold"),
}


def apply_styles():
    """Apply global ttk styles."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
        background=T["row_odd"], foreground=T["text"],
        fieldbackground=T["row_odd"], rowheight=34,
        font=FONT["body"], borderwidth=0, relief="flat")
    style.configure("Treeview.Heading",
        background=T["heading_bg"], foreground=T["muted"],
        font=FONT["label"], relief="flat", borderwidth=0, padding=(8, 6))
    style.map("Treeview",
        background=[("selected", T["row_sel"])],
        foreground=[("selected", T["accent"])])
    style.map("Treeview.Heading",
        background=[("active", T["border"])])
    style.configure("Vertical.TScrollbar",
        background=T["border"], troughcolor=T["bg"],
        arrowcolor=T["muted"], borderwidth=0, gripcount=0, width=8)
    style.map("Vertical.TScrollbar",
        background=[("active", T["border2"])])
    style.configure("TCombobox",
        fieldbackground=T["entry_bg"], background=T["panel"],
        foreground=T["entry_fg"], arrowcolor=T["accent"],
        borderwidth=1, relief="flat",
        selectbackground=T["accent_lt"],
        selectforeground=T["text"], padding=(8, 6))
    style.map("TCombobox",
        fieldbackground=[("readonly", T["entry_bg"])],
        foreground=[("readonly", T["entry_fg"])],
        selectbackground=[("readonly", T["accent_lt"])])
