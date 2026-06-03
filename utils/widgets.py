from tkinter import *
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
