import os
import sys
from tkinter import *
from utils.theme import T, FONT, apply_styles
from models.user_database import UserDatabase
from views.dashboard import build_dashboard_page
from views.inpatient_registration import build_inpatient_registration_page
from views.user_registration import build_user_registration_page
from views.user_management import build_user_management_page
from views.patient_registration import build_patient_registration_page
from views.search_patient import build_search_patient_page
from views.manual_patient_registration import build_manual_registration_page
from views.er_patient_registration import build_er_patient_registration_page
from views.er_report import build_er_report_page


# ── Global state ──────────────────────────────────────────
window        = None
page_container = None
pages          = {}
page_refreshers = {}
_shared_user_db = None


def resource_path(relative_path):
    """Get absolute path to resource, supporting PyInstaller bundles."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_user_db():
    """Return a shared UserDatabase instance, creating it if needed."""
    global _shared_user_db
    if _shared_user_db is None:
        _shared_user_db = UserDatabase()
    return _shared_user_db


def hide_all_pages():
    for page in pages.values():
        page.pack_forget()


def show_page(page_name):
    hide_all_pages()
    page = pages.get(page_name)
    if page:
        page.pack(fill=BOTH, expand=True)


# ── Navigation helpers ────────────────────────────────────

def open_dashboard(user_data):
    if 'dashboard' not in pages:
        pages['dashboard'] = build_dashboard_page(page_container, user_data, get_user_db, page_refreshers)
    else:
        refresher = page_refreshers.get('dashboard')
        if refresher:
            pages['dashboard'].destroy()
            pages['dashboard'] = refresher(page_container, user_data, get_user_db, page_refreshers)
    show_page('dashboard')


def open_patient_registration(user_data):
    if 'patient_registration' not in pages:
        pages['patient_registration'] = build_patient_registration_page(
            page_container, user_data, page_refreshers)
    show_page('patient_registration')

def open_er_patient_registration(user_data):
    if 'er_patient_registration' not in pages:
        pages['er_patient_registration'] = build_er_patient_registration_page(
            page_container, user_data, page_refreshers)
    show_page('er_patient_registration')


def open_er_report(user_data):
    if 'er_report' not in pages:
        pages['er_report'] = build_er_report_page(page_container, page_refreshers)
    else:
        refresher = page_refreshers.get('er_report')
        if refresher:
            pages['er_report'].destroy()
            pages['er_report'] = refresher(page_container, page_refreshers)
    show_page('er_report')


def open_search_patient():
    if 'search_patient' not in pages:
        pages['search_patient'] = build_search_patient_page(page_container, page_refreshers)
    show_page('search_patient')
    # Trigger refresh every time the page is opened
    r = page_refreshers.get("search_patient")
    if r:
        r()

def open_inpatient_registration(user_data):
    if 'inpatient_registration' not in pages:
        pages['inpatient_registration'] = build_inpatient_registration_page(
            page_container, user_data, page_refreshers)
    show_page('inpatient_registration')        

def open_user_registration():
    if 'user_registration' not in pages:
        pages['user_registration'] = build_user_registration_page(page_container, get_user_db)
    show_page('user_registration')


def open_user_management():
    if 'user_management' not in pages:
        pages['user_management'] = build_user_management_page(page_container, get_user_db)
    show_page('user_management')


def open_manual_registration(user_data):
    if 'manual_registration' not in pages:
        pages['manual_registration'] = build_manual_registration_page(
            page_container, user_data, page_refreshers)
    show_page('manual_registration')


# ── Main window ───────────────────────────────────────────

def create_main_application(user_data):
    global window, page_container

    window = Tk()
    window.title(f"Hospital Information System  —  {user_data['username']}")
    window.geometry("1280x800")
    window.minsize(960, 640)
    window.configure(bg=T["bg"])
    window.resizable(True, True)

    try:
        window.iconbitmap(resource_path("qphn.ico"))
    except Exception:
        try:
            icon = PhotoImage(file=resource_path("qphn.jpg"))
            window.iconphoto(True, icon)
        except Exception:
            pass

    apply_styles()

    # ── Top bar ───────────────────────────────────────────
    topbar = Frame(window, bg=T["panel"],
                   highlightthickness=1, highlightbackground=T["border"])
    topbar.pack(fill=X)

    Frame(topbar, bg=T["accent"], width=4).pack(side=LEFT, fill=Y)

    badge = Frame(topbar, bg=T["accent"], width=36, height=36)
    badge.pack_propagate(False)
    badge.pack(side=LEFT, padx=(14, 12), pady=10)
    Label(badge, text="H", font=("Georgia", 15, "bold"),
          bg=T["accent"], fg=T["white"]).place(relx=0.5, rely=0.5, anchor=CENTER)

    Label(topbar, text="Hospital Information System",
          font=("Georgia", 13, "bold"),
          bg=T["panel"], fg=T["text"]).pack(side=LEFT)

    right_bar = Frame(topbar, bg=T["panel"])
    right_bar.pack(side=RIGHT, padx=20, pady=8)

    role_badge = Frame(right_bar, bg=T["accent_lt"],
                       highlightthickness=1, highlightbackground=T["accent"])
    role_badge.pack(side=RIGHT, padx=(8, 0))
    Label(role_badge, text=user_data.get("role", "Staff"),
          font=FONT["tag"], bg=T["accent_lt"], fg=T["accent"],
          padx=8, pady=3).pack()

    Label(right_bar, text=user_data["username"],
          font=FONT["body_b"], bg=T["panel"], fg=T["text"]).pack(side=RIGHT)
    Label(right_bar, text="Logged in as  ",
          font=FONT["small"], bg=T["panel"], fg=T["muted"]).pack(side=RIGHT)

    # ── Body ──────────────────────────────────────────────
    body = Frame(window, bg=T["bg"])
    body.pack(fill=BOTH, expand=True)
    body.rowconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)

    # ── Sidebar ───────────────────────────────────────────
    sidebar = Frame(body, bg=T["sidebar"], width=228)
    sidebar.pack(side=LEFT, fill=Y)
    sidebar.pack_propagate(False)

    sh = Frame(sidebar, bg=T["sidebar"])
    sh.pack(fill=X, padx=16, pady=(18, 6))
    Label(sh, text="NAVIGATION", font=FONT["tag"],
          bg=T["sidebar"], fg="#4a6080").pack(anchor=W)
    Frame(sidebar, bg="#2a3f5c", height=1).pack(fill=X, padx=16, pady=(0, 8))

    active_nav = [None]

    def nav_btn(text, icon, command, section=False, danger=False):
        if section:
            Frame(sidebar, bg="#2a3f5c", height=1).pack(fill=X, padx=16, pady=(8, 4))
            Label(sidebar, text=text.upper(), font=FONT["tag"],
                  bg=T["sidebar"], fg="#4a6080").pack(anchor=W, padx=18, pady=(2, 4))
            return None

        norm_bg  = T["sidebar"]
        hover_bg = T["sidebar2"]
        act_bg   = T["accent"]

        f = Frame(sidebar, bg=norm_bg, cursor="hand2")
        f.pack(fill=X, padx=8, pady=2)

        accent_bar = Frame(f, bg=norm_bg, width=3)
        accent_bar.pack(side=LEFT, fill=Y)

        inner = Frame(f, bg=norm_bg)
        inner.pack(fill=X, padx=(8, 12), pady=9)

        ic_color = T["danger"] if danger else "#7ba7cc"
        tx_color = T["danger"] if danger else "#c8d8e8"

        ic_lbl = Label(inner, text=icon, font=("Calibri", 12), bg=norm_bg, fg=ic_color)
        ic_lbl.pack(side=LEFT)
        tx_lbl = Label(inner, text=text, font=FONT["nav"], bg=norm_bg, fg=tx_color)
        tx_lbl.pack(side=LEFT, padx=(10, 0))

        def on_enter(e):
            if active_nav[0] is not f:
                for w in [f, inner, ic_lbl, tx_lbl, accent_bar]:
                    w.config(bg=hover_bg)

        def on_leave(e):
            if active_nav[0] is not f:
                for w in [f, inner, ic_lbl, tx_lbl, accent_bar]:
                    w.config(bg=norm_bg)

        def on_click(e=None):
            if active_nav[0] and active_nav[0] is not f:
                prev = active_nav[0]
                for w in prev.winfo_children():
                    w.config(bg=norm_bg)
                    for ww in w.winfo_children():
                        try:
                            ww.config(bg=norm_bg)
                        except Exception:
                            pass
                prev.config(bg=norm_bg)
            if not danger:
                active_nav[0] = f
                for w in [f, inner, ic_lbl, tx_lbl]:
                    w.config(bg=act_bg)
                accent_bar.config(bg=T["white"])
                tx_lbl.config(fg=T["white"])
                ic_lbl.config(fg=T["white"])
            command()

        for w in [f, inner, ic_lbl, tx_lbl, accent_bar]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        return f

    db_btn   = nav_btn("Dashboard",            "⊞", lambda: open_dashboard(user_data))
    nav_btn("Out-Patient Registration", "＋", lambda: open_patient_registration(user_data))
    nav_btn("ER Patient Registration", "＋", lambda: open_er_patient_registration(user_data))
    nav_btn("Search Patient",       "⌕", open_search_patient)
    nav_btn("In-Patient",            "🛏", lambda: open_inpatient_registration(user_data))

    if user_data.get("role") == "Administrator":
        nav_btn("Administration", "", None, section=True)
        nav_btn("ER Report",         "📄", lambda: open_er_report(user_data))
        nav_btn("Manual Registration", "✎", lambda: open_manual_registration(user_data))
        nav_btn("User Registration",   "⊕", open_user_registration)
        nav_btn("User Management",     "⊞", open_user_management)

    Frame(sidebar, bg=T["sidebar"]).pack(fill=BOTH, expand=True)
    Frame(sidebar, bg="#2a3f5c", height=1).pack(fill=X, padx=16, pady=(0, 4))
    nav_btn("Exit Application", "⏻", window.quit, danger=True)
    Frame(sidebar, bg=T["sidebar"], height=8).pack(fill=X)

        # Add a watermark below the exit button:
    Frame(sidebar, bg=T["sidebar"], height=8).pack(fill=X)
    Label(sidebar,
        text="© 2026 Surio / QPHN - Bonpen",
        font=("Calibri", 7), bg=T["sidebar"],
        fg="#2a3f5c").pack(pady=(0, 6))
    Label(sidebar,
        text="v1.0.0",
        font=("Calibri", 7), bg=T["sidebar"],
        fg="#2a3f5c").pack(pady=(0, 8))
    
    # ── Content area ──────────────────────────────────────
    content = Frame(body, bg=T["bg"])
    content.pack(side=LEFT, fill=BOTH, expand=True)

    page_container = Frame(content, bg=T["bg"])
    page_container.pack(fill=BOTH, expand=True)

    pages["dashboard"]            = build_dashboard_page(page_container, user_data, get_user_db, page_refreshers)
    pages["patient_registration"] = build_patient_registration_page(page_container, user_data, page_refreshers)
    pages["search_patient"]       = build_search_patient_page(page_container, page_refreshers)
    if user_data.get("role") == "Administrator":
        pages["er_report"]           = build_er_report_page(page_container)
        pages["user_registration"]   = build_user_registration_page(page_container, get_user_db)
        pages["user_management"]     = build_user_management_page(page_container, get_user_db)
        pages["manual_registration"] = build_manual_registration_page(page_container, user_data, page_refreshers)

    if db_btn:
        db_btn.event_generate("<Button-1>")

    show_page("dashboard")
    window.mainloop()
