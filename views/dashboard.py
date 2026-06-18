from tkinter import *
from tkinter import ttk
from utils.theme import T, FONT
from utils.widgets import page_header, stat_card
from models.patient_database import PatientDatabase


def build_dashboard_page(parent, user_data, get_user_db, page_refreshers):
    """Build the main dashboard page with stat cards and recent patients table."""
    frame = Frame(parent, bg=T["bg"])

    db = PatientDatabase()
    patients = db.get_all_patients()
    total_patients = len(patients)
    recent_patients = sorted(
        patients.values(),
        key=lambda item: item.get('registration_date') or '',
        reverse=True
    )[:20]

    total_users = 0
    if user_data.get('role') == 'Administrator':
        user_db = get_user_db()
        total_users = len(user_db.get_all_users())

    page_header(frame, "Dashboard",
                f"Welcome, {user_data['username']}  ·  {user_data['role']}")

    cards_row = Frame(frame, bg=T["bg"])
    cards_row.pack(fill=X, padx=24, pady=(18, 0))

    c1 = stat_card(cards_row, "Total Patients", str(total_patients), "Registered in the system")
    c1.pack(side=LEFT, expand=True, fill=X, padx=(0, 10))

    if user_data.get("role") == "Administrator":
        c2 = stat_card(cards_row, "System Users", str(total_users), "Active user accounts")
    else:
        c2 = stat_card(cards_row, "Your Role", user_data.get("role", "Staff"), "Access level")
    c2.pack(side=LEFT, expand=True, fill=X, padx=(0, 10))

    c3 = stat_card(cards_row, "Recent Registrations", str(len(recent_patients)), "Latest patient records")
    c3.pack(side=LEFT, expand=True, fill=X)

    tbl_card = Frame(frame, bg=T["card"],
                     highlightthickness=1, highlightbackground=T["border"])
    tbl_card.pack(fill=BOTH, expand=True, padx=24, pady=18)

    Label(tbl_card, text="RECENT PATIENTS", font=("Helvetica", 9, "bold"),
          bg=T["card"], fg=T["accent"]).pack(anchor=W, padx=16, pady=(14, 4))
    Frame(tbl_card, bg=T["border"], height=1).pack(fill=X, padx=16, pady=(0, 8))

    tf = Frame(tbl_card, bg=T["card"])
    tf.pack(fill=BOTH, expand=True, padx=16, pady=(0, 16))

    columns = ("ID", "Name", "Gender", "Registered By")
    tree = ttk.Treeview(tf, columns=columns, show="headings", height=14)
    tree.heading("ID",            text="Patient ID")
    tree.heading("Name",          text="Full Name")
    tree.heading("Gender",        text="Gender")
    tree.heading("Registered By", text="Registered By")
    tree.column("ID",            width=110, anchor=CENTER)
    tree.column("Name",          width=280, anchor=W)
    tree.column("Gender",        width=90,  anchor=CENTER)
    tree.column("Registered By", width=180, anchor=CENTER)

    sb = ttk.Scrollbar(tf, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True)
    sb.pack(side=RIGHT, fill=Y)

    for i, pd in enumerate(recent_patients):
        full_name = f"{pd.get('first_name','')} {pd.get('middle_name','')} {pd.get('last_name','')}".strip().title()
        tag = "alt" if i % 2 else ""
        tree.insert("", END, tags=(tag,), values=(
            pd.get("patient_id", "N/A"), full_name,
            (pd.get("gender") or "N/A").upper(),
            (pd.get("registered_by") or "N/A").title()
        ))
    tree.tag_configure("alt", background=T["row_alt"])

    page_refreshers["dashboard"] = lambda *args, **kwargs: _refresh(parent, user_data, get_user_db, page_refreshers)
    return frame


def _refresh(parent, user_data, get_user_db, page_refreshers):
    """Rebuild dashboard frame in-place."""
    # This is called from the refresher; caller must replace pages['dashboard']
    return build_dashboard_page(parent, user_data, get_user_db, page_refreshers)
