import os
import sys
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.theme import T, FONT
from utils.widgets import mk_entry, mk_btn, mk_combo, page_header, section_label
from utils.validators import (
    validate_email, validate_date,
    uppercase_entry_widget, format_birthdate_entry
)
from models.patient_database import PatientDatabase

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None


def build_patient_registration_page(parent, user_data, page_refreshers):
    """Build the patient registration page and form."""
    frame = Frame(parent, bg=T["bg"])
    frame.rowconfigure(1, weight=1)
    frame.columnconfigure(0, weight=1)
    db = PatientDatabase()

    page_header(frame, "Patient Registration", "Register a new patient into the system")

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

    # Bind mousewheel only while hovering over the canvas
    def _on_mousewheel(e):
        canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))    

    outer = Frame(cf, bg=T["bg"])
    outer.pack(fill=BOTH, expand=True, padx=24, pady=16)
    outer.columnconfigure(0, weight=1)

    # Patient ID badge
    id_card = Frame(outer, bg=T["panel"],
                    highlightthickness=1, highlightbackground=T["border"])
    id_card.pack(fill=X, pady=(0, 14))
    id_inner = Frame(id_card, bg=T["panel"])
    id_inner.pack(fill=X, padx=20, pady=12)
    Label(id_inner, text="ASSIGNED PATIENT ID",
          font=FONT["tag"], bg=T["panel"], fg=T["muted"]).pack(side=LEFT, padx=(0, 16))
    patient_id_label = Label(id_inner, text="Assign on save",
                             font=FONT["mono"],
                             bg=T["accent_lt"], fg=T["accent"],
                             padx=14, pady=4,
                             highlightthickness=1, highlightbackground=T["accent"])
    patient_id_label.pack(side=LEFT)

    def section(title):
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
            w = DateEntry(grid, width=24, date_pattern="mm-dd-yyyy", font=FONT["body"],
                          background=T["accent"], foreground=T["white"],
                          headersbackground=T["accent"])
            w.grid(row=row*2+1, column=c, sticky=EW,
                   padx=(0 if c == 0 else 16, 16))
            w.bind("<KeyRelease>", lambda e, x=w: format_birthdate_entry(x))
        else:
            w = mk_entry(grid, width=24, show=show)
            w.grid(row=row*2+1, column=c, sticky=EW, ipady=7,
                   padx=(0 if c == 0 else 16, 16))
            if not show and not date:
                w.bind("<KeyRelease>", lambda e, x=w: uppercase_entry_widget(x))
            if date:
                w.bind("<KeyRelease>", lambda e, x=w: format_birthdate_entry(x))
        return w

    # Personal info
    g1 = section("Personal Information")
    name_entry        = fld(g1, "First Name",   0, 0)
    middle_name_entry = fld(g1, "Middle Name",  0, 2)
    last_name_entry   = fld(g1, "Last Name",    1, 0)
    gender_var        = StringVar(value="MALE")
    fld(g1, "Gender",       2, 0, combo_var=gender_var, combo_vals=["MALE", "FEMALE", "OTHER"])
    civil_status_var  = StringVar(value="SINGLE")
    fld(g1, "Civil Status", 2, 2, combo_var=civil_status_var,
        combo_vals=["SINGLE", "MARRIED", "WIDOWED", "DIVORCED"])
    nationality_entry = fld(g1, "Nationality",   3, 0)
    nationality_entry.insert(0, "FILIPINO")
    birth_date_entry  = fld(g1, "Birth Date",   3, 2, date=True)
    birth_place_entry = fld(g1, "Birth Place",  4, 0)

    # Contact info
    g2 = section("Contact Information")
    phone_entry       = fld(g2, "Phone Number",      0, 0)
    email_entry       = fld(g2, "Email Address",     0, 2)
    barangay_entry    = fld(g2, "Barangay",          1, 0)
    municipality_entry= fld(g2, "Municipality",      1, 2)
    municipality_entry.insert(0, "CATANAUAN")
    province_entry    = fld(g2, "Province",          2, 0)
    province_entry.insert(0, "QUEZON")
    emergency_entry   = fld(g2, "Emergency Contact", 2, 2)

    def clear_patient_form():
        for w in [name_entry, middle_name_entry, last_name_entry,
                  phone_entry, email_entry, barangay_entry, municipality_entry,
                  province_entry, birth_place_entry, emergency_entry]:
            w.delete(0, END)
        municipality_entry.insert(0, "CATANAUAN")
        province_entry.insert(0, "QUEZON")
        if hasattr(birth_date_entry, "set_date"):
            birth_date_entry.set_date(datetime.today())
        else:
            birth_date_entry.delete(0, END)
        civil_status_var.set("SINGLE")
        gender_var.set("MALE")

    def register_patient(force=False):
        first_name = name_entry.get().strip()
        last_name  = last_name_entry.get().strip()

        if not first_name or not last_name:
            messagebox.showerror("Error", "First Name and Last Name are required")
            return
        if email_entry.get().strip() and not validate_email(email_entry.get()):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        birth_date_value = birth_date_entry.get().strip()
        if birth_date_value and not validate_date(birth_date_value):
            messagebox.showerror("Error", "Birth date must be in MM-DD-YYYY format")
            return

        patient_data = {
            "first_name":    first_name.upper(),
            "middle_name":   middle_name_entry.get().strip().upper(),
            "last_name":     last_name.upper(),
            "gender":        gender_var.get().upper(),
            "birth_date":    birth_date_value or None,
            "birth_place":   birth_place_entry.get().strip().upper(),
            "civil_status":  civil_status_var.get().upper(),
            "nationality":   nationality_entry.get().strip().upper(),
            "municipality":  municipality_entry.get().strip().upper(),
            "province":      province_entry.get().strip().upper(),
            "registered_by": (user_data.get("username") if user_data else "").upper(),
            "phone":         phone_entry.get().strip().upper(),
            "email":         email_entry.get().strip(),
            "barangay":      barangay_entry.get().strip().upper(),
            "medical_history": ""
        }

        if not force and db.has_duplicate_patient(patient_data):
            messagebox.showwarning("Duplicate Patient",
                "A patient with the same name/birth date already exists.\n"
                "Use Save Anyway to proceed.")
            return
        if force and not messagebox.askyesno("Confirm", "Duplicate detected. Save anyway?"):
            return

        assigned_patient_id = db.add_patient(patient_data)
        if not assigned_patient_id:
            messagebox.showerror("Error",
                "Unable to register patient. Please try again.")
            return

        patient_id_label.config(text=assigned_patient_id)
        messagebox.showinfo("Registered",
            f"Patient {first_name} {last_name} registered.\nID: {assigned_patient_id}")

        for key in ("patient_list", "dashboard"):
            r = page_refreshers.get(key)
            if r:
                r()

        patient_id_label.config(text="Assign on save")
        clear_patient_form()

    bf = Frame(outer, bg=T["bg"])
    bf.pack(pady=(4, 20), anchor=W)
    mk_btn(bf, "Register Patient", register_patient, width=18).pack(side=LEFT, padx=(0, 8))
    mk_btn(bf, "Save Anyway", lambda: register_patient(force=True),
           color=T["warning"], width=14).pack(side=LEFT, padx=(0, 8))
    mk_btn(bf, "Clear Form", clear_patient_form, secondary=True, width=12).pack(side=LEFT)

    return frame
