from tkinter import *
import json
import os
from tkinter import ttk
from utils.theme import T, FONT


def mk_entry(parent, width=28, show=None, textvariable=None, readonly=False):
    """Create a styled Entry widget."""
    kw = dict(
        width=width, font=FONT["body"],
        bg=T["entry_bg"], fg=T["entry_fg"],
        insertbackground=T["accent"],
        relief="flat", bd=0,
        highlightthickness=1,
        highlightbackground=T["border2"],
        highlightcolor=T["accent"],
        selectbackground=T["accent_lt"],
        selectforeground=T["text"],
    )
    if show:
        kw["show"] = show
    if textvariable:
        kw["textvariable"] = textvariable
    if readonly:
        kw["state"] = "readonly"
        kw["bg"] = T["border"]
        kw["fg"] = T["muted"]
    return Entry(parent, **kw)


def mk_btn(parent, text, command, color=None, width=14, danger=False, secondary=False):
    """Create a styled Button widget."""
    if danger:
        bg, fg, abg = T["danger"], T["white"], "#b91c1c"
    elif secondary:
        bg, fg, abg = T["border"], T["text"], T["border2"]
    else:
        bg, fg, abg = (color or T["accent"]), T["white"], T["accent_h"]
    return Button(parent, text=text, command=command,
                  bg=bg, fg=fg, font=FONT["body_b"],
                  activebackground=abg, activeforeground=fg,
                  bd=0, relief=FLAT, width=width,
                  padx=12, pady=8, cursor="hand2")


def mk_combo(parent, textvariable, values, width=27):
    """Create a styled readonly Combobox widget."""
    return ttk.Combobox(parent, textvariable=textvariable,
                        values=values, width=width, state="readonly",
                        font=FONT["body"])


def page_header(parent, title, subtitle=""):
    """Render a page header with title and optional subtitle."""
    hf = Frame(parent, bg=T["panel"])
    hf.pack(fill=X)
    Frame(hf, bg=T["accent"], height=3).pack(fill=X)
    inner = Frame(hf, bg=T["panel"])
    inner.pack(fill=X, padx=28, pady=(16, 14))
    Label(inner, text=title, font=FONT["h1"],
          bg=T["panel"], fg=T["text"]).pack(anchor=W)
    if subtitle:
        Label(inner, text=subtitle, font=FONT["body"],
              bg=T["panel"], fg=T["muted"]).pack(anchor=W, pady=(2, 0))
    Frame(hf, bg=T["border"], height=1).pack(fill=X)


def field_card(parent, **pack_kw):
    """Create a bordered card frame."""
    f = Frame(parent, bg=T["panel"],
              highlightthickness=1, highlightbackground=T["border"])
    f.pack(**pack_kw)
    return f


def section_label(parent, text):
    """Render an accented section label with a divider."""
    Label(parent, text=text.upper(), font=FONT["tag"],
          bg=T["panel"], fg=T["accent"]).pack(anchor=W, padx=20, pady=(14, 2))
    Frame(parent, bg=T["border"], height=1).pack(fill=X, padx=20, pady=(0, 8))


def stat_card(parent, title, value, icon="", color=None):
    """Create a statistics summary card widget."""
    c = color or T["accent"]
    f = Frame(parent, bg=T["panel"],
              highlightthickness=1, highlightbackground=T["border"])
    top = Frame(f, bg=T["panel"])
    top.pack(fill=X, padx=20, pady=(18, 4))
    Label(top, text=icon, font=("Calibri", 18),
          bg=T["panel"], fg=c).pack(side=LEFT, padx=(0, 10))
    Label(top, text=value, font=("Georgia", 28, "bold"),
          bg=T["panel"], fg=c).pack(side=LEFT)
    Label(f, text=title, font=FONT["body_b"],
          bg=T["panel"], fg=T["text"]).pack(anchor=W, padx=20)
    Frame(f, bg=c, height=3).pack(fill=X, pady=(14, 0))
    return f

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "input_history.json")

def load_all_history():
    """Load all history stores from JSON file on startup."""
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Could not load input history: {e}")
    return {}

def save_all_history(histories: dict):
    """Save all history stores to JSON file."""
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, "w") as f:
            json.dump(histories, f, indent=2)
    except Exception as e:
        print(f"Could not save input history: {e}")

def add_input_history(entry_widget, history_store, history_key, all_histories):
    """
    Attach Up/Down arrow key history navigation to an Entry widget.
    Persists history to JSON automatically on each save.
    """
    index = [-1]

    def on_up(event):
        if not history_store:
            return
        if index[0] < len(history_store) - 1:
            index[0] += 1
        entry_widget.delete(0, END)
        entry_widget.insert(0, history_store[index[0]])

    def on_down(event):
        if index[0] <= 0:
            index[0] = -1
            entry_widget.delete(0, END)
            return
        index[0] -= 1
        entry_widget.delete(0, END)
        entry_widget.insert(0, history_store[index[0]])

    def on_keypress(event):
        index[0] = -1

    entry_widget.bind("<Up>",       on_up)
    entry_widget.bind("<Down>",     on_down)
    entry_widget.bind("<KeyPress>", on_keypress)

    def save(value):
        """Add value to history and persist to disk."""
        value = value.strip()
        if value and (not history_store or history_store[0] != value):
            history_store.insert(0, value)
            if len(history_store) > 20:
                history_store.pop()
            # Keep all_histories dict in sync and write to disk
            all_histories[history_key] = history_store
            save_all_history(all_histories)

    return save