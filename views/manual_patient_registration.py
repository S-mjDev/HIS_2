from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
from utils.theme import T, FONT
from utils.widgets import mk_entry, mk_btn, mk_combo, page_header, section_label
from utils.validators import (
    validate_date, uppercase_entry_widget, format_birthdate_entry
)
from models.patient_database import PatientDatabase

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None


def build_manual_registration_page(parent, user_data, page_refreshers):
    """Admin-only page: register a patient with a manually assigned patient ID."""
    frame = Frame(parent, bg=T["bg"])
    frame.rowconfigure(1, weight=1)
    frame.columnconfigure(0, weight=1)
    db = PatientDatabase()

    page_header(
        frame,
        "Manual Patient Registration",
        "Administrator only — assign a custom Patient ID manually"
    )

    canvas = Canvas(frame, bg=T["bg"], highlightthickness=0)
    sb = ttk.Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
    sb.pack(side=RIGHT, fill=Y)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    canvas.configure(yscrollcommand=sb.set)

    cf = Frame(canvas, bg=T["bg"])
    cw = canvas.create_window((0, 0), window=cf, anchor="nw")

    def _resize_cf(e): canvas.configure(scrollregion=canvas.bbox("all"))
    def _resize_cw(e): canvas.itemconfig(cw, width=e.width)
    cf.bind("<Configure>", _resize_cf)
    canvas.bind("<Configure>", _resize_cw)
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    outer = Frame(cf, bg=T["bg"])
    outer.pack(fill=BOTH, expand=True, padx=24, pady=16)
    outer.columnconfigure(0, weight=1)

    # ── Admin notice banner ───────────────────────────────
    notice = Frame(outer, bg=T["warning"],
                   highlightthickness=1, highlightbackground=T["warning"])
    notice.pack(fill=X, pady=(0, 14))
    notice_inner = Frame(notice, bg="#fffbeb")
    notice_inner.pack(fill=X, padx=2, pady=2)
    Label(notice_inner,
          text="⚠  Administrator Access Only  —  The Patient ID entered below will be saved exactly as typed.",
          font=FONT["body_b"], bg="#fffbeb", fg=T["warning"],
          padx=16, pady=10).pack(anchor=W)

    # ── Manual Patient ID input card ──────────────────────
    id_card = Frame(outer, bg=T["panel"],
                    highlightthickness=1, highlightbackground=T["border"])
    id_card.pack(fill=X, pady=(0, 14))
    section_label(id_card, "Manual Patient ID Assignment")

    id_body = Frame(id_card, bg=T["panel"])
    id_body.pack(fill=X, padx=20, pady=(0, 16))
    id_body.columnconfigure(1, weight=0)

    Label(id_body, text="PATIENT ID", font=FONT["tag"],
          bg=T["panel"], fg=T["muted"]).grid(row=0, column=0, sticky=W, pady=(0, 4), padx=(0, 16))

    patient_id_var = StringVar()
    patient_id_entry = mk_entry(id_body, width=20)
    patient_id_entry.config(textvariable=patient_id_var)
    patient_id_entry.grid(row=1, column=0, sticky=W, ipady=8, padx=(0, 16))

    id_status_lbl = Label(id_body, text="", font=FONT["small"],
                          bg=T["panel"], fg=T["muted"])
    id_status_lbl.grid(row=1, column=1, sticky=W)

    def check_id(*_):
        pid = patient_id_var.get().strip()
        if not pid:
            id_status_lbl.config(text="", fg=T["muted"])
            return
        if db.patient_exists(pid):
            id_status_lbl.config(text="✗  ID already in use", fg=T["danger"])
        else:
            id_status_lbl.config(text="✓  ID is available", fg=T["success"])

    patient_id_entry.bind("<KeyRelease>", check_id)

    # ── Shared field builder ──────────────────────────────
    def section_card(title):
        c = Frame(outer, bg=T["panel"],
                  highlightthickness=1, highlightbackground=T["border"])
        c.pack(fill=X, pady=(0, 12))
        section_label(c, title)
        g = Frame(c, bg=T["panel"])
        g.pack(fill=X, padx=20, pady=(0, 16))
        g.columnconfigure(1, weight=1)
        g.columnconfigure(3, weight=1)
        return g

    def fld(grid, label, row, col=0, combo_var=None, combo_vals=None, show=None, date=False):
        c = col
        Label(grid, text=label.upper(), font=FONT["tag"],
              bg=T["panel"], fg=T["muted"]).grid(
            row=row*2, column=c, sticky=W, pady=(10, 3), padx=(0 if c == 0 else 16, 8))
        if combo_var and combo_vals:
            w = mk_combo(grid, combo_var, combo_vals, width=24)
            w.grid(row=row*2+1, column=c, sticky=EW, ipady=6,
                   padx=(0 if c == 0 else 16, 16))
        elif date and DateEntry:
            w = DateEntry(grid, width=24, date_pattern="yyyy-mm-dd", font=FONT["body"],
                          background=T["accent"], foreground=T["white"],
                          headersbackground=T["accent"])
            w.grid(row=row*2+1, column=c, sticky=EW,
                   padx=(0 if c == 0 else 16, 16))
        else:
            w = mk_entry(grid, width=24, show=show)
            w.grid(row=row*2+1, column=c, sticky=EW, ipady=7,
                   padx=(0 if c == 0 else 16, 16))
            if not show and not date:
                w.bind("<KeyRelease>", lambda e, x=w: uppercase_entry_widget(x))
            if date and not DateEntry:
                w.bind("<KeyRelease>", lambda e, x=w: format_birthdate_entry(x))
        return w

    # ── Personal Information ──────────────────────────────
    g1 = section_card("Personal Information")
    name_entry        = fld(g1, "First Name",   0, 0)
    middle_name_entry = fld(g1, "Middle Name",  0, 2)
    last_name_entry   = fld(g1, "Last Name",    1, 0)
    gender_var        = StringVar(value="MALE")
    fld(g1, "Gender",       2, 0, combo_var=gender_var, combo_vals=["MALE", "FEMALE", "OTHER"])
    civil_status_var  = StringVar(value="SINGLE")
    fld(g1, "Civil Status", 2, 2, combo_var=civil_status_var,
        combo_vals=["SINGLE", "MARRIED", "WIDOWED", "DIVORCED"])
    nationality_entry = fld(g1, "Nationality",  3, 0)
    birth_date_entry  = fld(g1, "Birth Date",   3, 2, date=True)
    birth_place_entry = fld(g1, "Birth Place",  4, 0)

    # Contact info
    g2 = section_card("Contact Information")
    phone_entry       = fld(g2, "Phone Number",      0, 0)
    email_entry       = fld(g2, "Email Address",     0, 2)
    barangay_entry    = fld(g2, "Barangay",          1, 0)
    municipality_entry= fld(g2, "Municipality",      1, 2)
    municipality_entry.insert(0, "CATANAUAN")
    province_entry    = fld(g2, "Province",          2, 0)
    province_entry.insert(0, "QUEZON")
    emergency_entry   = fld(g2, "Emergency Contact", 2, 2)

    # ── Form actions ──────────────────────────────────────
    def clear_form():
        patient_id_entry.delete(0, END)
        id_status_lbl.config(text="", fg=T["muted"])
        for w in [name_entry, middle_name_entry, last_name_entry,
                  phone_entry, email_entry, birth_place_entry,
                  nationality_entry, emergency_entry, barangay_entry]:
            w.delete(0, END)
        if hasattr(birth_date_entry, "set_date"):
            birth_date_entry.set_date(datetime.today())
        else:
            birth_date_entry.delete(0, END)
        civil_status_var.set("SINGLE")
        gender_var.set("MALE")

    def register_patient(force=False):
        patient_id = patient_id_var.get().strip()
        first_name = name_entry.get().strip()
        last_name  = last_name_entry.get().strip()

        # Validate patient ID
        if not patient_id:
            messagebox.showerror("Error", "Patient ID is required")
            patient_id_entry.focus()
            return
        if db.patient_exists(patient_id):
            messagebox.showerror(
                "ID Conflict",
                f"Patient ID '{patient_id}' is already in use.\nPlease enter a different ID."
            )
            patient_id_entry.focus()
            return

        # Validate patient fields
        if not first_name or not last_name:
            messagebox.showerror("Error", "First Name and Last Name are required")
            return
        
        birth_date_value = birth_date_entry.get().strip()
        if birth_date_value and not validate_date(birth_date_value):
            messagebox.showerror("Error", "Birth date must be in YYYY-MM-DD format")
            return

        patient_data = {
            "first_name":      first_name.upper(),
            "middle_name":     middle_name_entry.get().strip().upper(),
            "last_name":       last_name.upper(),
            "gender":          gender_var.get().upper(),
            "birth_date":      birth_date_value or None,
            "birth_place":     birth_place_entry.get().strip().upper(),
            "civil_status":    civil_status_var.get().upper(),
            "nationality":     nationality_entry.get().strip().upper(),
            "registered_by":   (user_data.get("username") if user_data else "").upper(),
            "phone":           phone_entry.get().strip().upper(),
            "email":           email_entry.get().strip().upper(),
            "barangay":        barangay_entry.get().strip().upper(),
            "municipality":    municipality_entry.get().strip().upper(),
            "province":        province_entry.get().strip().upper(),
            "medical_history": ""
        }

        if not force and db.has_duplicate_patient(patient_data):
            messagebox.showwarning(
                "Duplicate Patient",
                "A patient with the same name/birth date already exists.\n"
                "Use Save Anyway to proceed."
            )
            return
        if force and not messagebox.askyesno("Confirm", "Duplicate detected. Save anyway?"):
            return

        patient_data["patient_id"] = patient_id
        try:
            result = db.add_patient(patient_id, patient_data)
        except TypeError:
            result = db.add_patient(patient_data)

        if result:
            messagebox.showinfo(
                "Registered",
                f"Patient {first_name} {last_name} registered.\nAssigned ID: {patient_id}"
            )
            for key in ("patient_list", "dashboard"):
                r = page_refreshers.get(key)
                if r:
                    r()
            clear_form()
        else:
            messagebox.showerror("Error", "Failed to register patient. Check the logs.")

    bf = Frame(outer, bg=T["bg"])
    bf.pack(pady=(4, 20), anchor=W)
    mk_btn(bf, "Register Patient", register_patient, width=18).pack(side=LEFT, padx=(0, 8))
    mk_btn(bf, "Save Anyway", lambda: register_patient(force=True),
           color=T["warning"], width=14).pack(side=LEFT, padx=(0, 8))
    mk_btn(bf, "Clear Form", clear_form, secondary=True, width=12).pack(side=LEFT)

    return frame
