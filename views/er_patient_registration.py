import os
import sys
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
from utils.widgets import add_input_history, load_all_history

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from utils.theme import T, FONT
from utils.widgets import mk_entry, mk_btn, mk_combo, page_header, section_label
from utils.validators import (
    validate_email, validate_date, format_birthdate_entry, format_time_entry
)
from models.patient_database import PatientDatabase

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None


def build_er_patient_registration_page(parent, user_data, page_refreshers):
    """Build the ER patient registration page and form."""
    frame = Frame(parent, bg=T["bg"])
    frame.rowconfigure(1, weight=1)
    frame.columnconfigure(0, weight=1)
    db = PatientDatabase()

    page_header(frame, "ER Patient Registration", "Register a new patient into the ER system")

    # ── Scrollable canvas (row 1) ─────────────────────────
    canvas = Canvas(frame, bg=T["bg"], highlightthickness=0)
    sb = ttk.Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side=RIGHT, fill=Y)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    cf = Frame(canvas, bg=T["bg"])
    cw = canvas.create_window((0, 0), window=cf, anchor="nw")

    def _resize_cf(e): canvas.configure(scrollregion=canvas.bbox("all"))
    def _resize_cw(e): canvas.itemconfig(cw, width=e.width)
    cf.bind("<Configure>", _resize_cf)
    canvas.bind("<Configure>", _resize_cw)
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def _on_mousewheel(e):
        canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    outer = Frame(cf, bg=T["bg"])
    outer.pack(fill=BOTH, expand=True, padx=24, pady=16)
    outer.columnconfigure(0, weight=1)

    # ── Patient ID + Case Number badge ────────────────────
    id_card = Frame(outer, bg=T["panel"],
                    highlightthickness=1, highlightbackground=T["border"])
    id_card.pack(fill=X, pady=(0, 16))
    id_inner = Frame(id_card, bg=T["panel"])
    id_inner.pack(fill=X, padx=20, pady=14)

    # Case Number
    cn_frame = Frame(id_inner, bg=T["success_lt"],
                     highlightthickness=1, highlightbackground=T["success"])
    cn_frame.pack(side=LEFT, padx=(0, 20))
    Label(cn_frame, text="CASE NO.", font=FONT["tag"],
          bg=T["success_lt"], fg=T["success"], padx=10, pady=2).pack(anchor=W)
    case_number_label = Label(cn_frame,
                              text=db.generate_next_case_number()
                                   if hasattr(db, 'generate_next_case_number')
                                   else "ER-AUTO",
                              font=FONT["mono"],
                              bg=T["success_lt"], fg=T["success"],
                              padx=10, pady=4)
    case_number_label.pack(anchor=W)

    # Patient ID
    pid_frame = Frame(id_inner, bg=T["accent_lt"],
                      highlightthickness=1, highlightbackground=T["accent"])
    pid_frame.pack(side=LEFT)
    Label(pid_frame, text="PATIENT ID", font=FONT["tag"],
          bg=T["accent_lt"], fg=T["accent"], padx=10, pady=2).pack(anchor=W)
    patient_id_label = Label(pid_frame, text="Assign on save",
                             font=FONT["mono"],
                             bg=T["accent_lt"], fg=T["accent"],
                             padx=10, pady=4)
    patient_id_label.pack(anchor=W)

    # Registered by (right side)
    reg_frame = Frame(id_inner, bg=T["panel"])
    reg_frame.pack(side=RIGHT)
    Label(reg_frame, text="REGISTERED BY", font=FONT["tag"],
          bg=T["panel"], fg=T["muted"]).pack(anchor=E)
    Label(reg_frame,
          text=(user_data.get("username") or "").upper(),
          font=FONT["body_b"], bg=T["panel"], fg=T["text"]).pack(anchor=E)
    Label(reg_frame,
          text=datetime.now().strftime("%B %d, %Y"),
          font=FONT["small"], bg=T["panel"], fg=T["muted"]).pack(anchor=E)

    def section(title, color=None):
        c = Frame(outer, bg=T["panel"],
                  highlightthickness=1, highlightbackground=T["border"])
        c.pack(fill=X, pady=(0, 12))
        # Colored section title bar
        bar = Frame(c, bg=color or T["accent"], height=2)
        bar.pack(fill=X)
        Label(c, text=title.upper(), font=FONT["tag"],
              bg=T["panel"], fg=color or T["accent"]).pack(
            anchor=W, padx=20, pady=(10, 2))
        Frame(c, bg=T["border"], height=1).pack(fill=X, padx=20, pady=(0, 8))
        g = Frame(c, bg=T["panel"])
        g.pack(fill=X, padx=20, pady=(0, 16))
        g.columnconfigure(0, weight=1)
        g.columnconfigure(1, weight=1)
        g.columnconfigure(2, weight=1)
        return g

    def fld(grid, label, row, col=0, combo_var=None, combo_vals=None, show=None, date=False, time_field=False, span=1):
        c = col
        px_l = 0 if c == 0 else 16
        Label(grid, text=label.upper(), font=FONT["tag"],
              bg=T["panel"], fg=T["muted"]).grid(
            row=row*2, column=c, sticky=W, pady=(10, 3), padx=(px_l, 8), columnspan=span)
        if combo_var and combo_vals:
            w = mk_combo(grid, combo_var, combo_vals, width=24)
            w.grid(row=row*2+1, column=c, sticky=EW, ipady=6,
                   padx=(0 if c == 0 else 16, 16), columnspan=span)
            if time_field or "TIME" in label.upper():
                w.bind("<KeyRelease>", lambda e, x=w: format_time_entry(x))
        elif date and DateEntry:
            w = DateEntry(grid, width=24, date_pattern="mm-dd-yyyy", font=FONT["body"],
                          background=T["accent"], foreground=T["white"],
                          headersbackground=T["accent"])
            w.grid(row=row*2+1, column=c, sticky=EW,
                   padx=(0 if c == 0 else 16, 16), columnspan=span)
            w.bind("<KeyRelease>", lambda e, x=w: format_birthdate_entry(x))
        else:
            w = mk_entry(grid, width=24, show=show)
            w.grid(row=row*2+1, column=c, sticky=EW, ipady=7,
                   padx=(0 if c == 0 else 16, 16), columnspan=span)
            if date:
                w.bind("<KeyRelease>", lambda e, x=w: format_birthdate_entry(x))
            if time_field or "TIME" in label.upper():
                w.bind("<KeyRelease>", lambda e, x=w: format_time_entry(x))
        return w

    g1 = section("Personal Information")
    name_entry        = fld(g1, "First Name",   0, 0)
    middle_name_entry = fld(g1, "Middle Name",  0, 1)
    last_name_entry   = fld(g1, "Last Name",    0, 2)
    gender_var = StringVar(value="MALE")
    # Radio buttons for gender
    Label(g1, text="GENDER", font=FONT["tag"],
          bg=T["panel"], fg=T["muted"]).grid(
        row=2, column=0, sticky=W, pady=(10, 3))
    gender_frame = Frame(g1, bg=T["panel"])
    gender_frame.grid(row=3, column=0, sticky=W, padx=(0, 16))
    for opt in ["MALE", "FEMALE"]:
        Radiobutton(gender_frame, text=opt, variable=gender_var, value=opt,
                    font=FONT["body"], bg=T["panel"], fg=T["text"],
                    activebackground=T["panel"], activeforeground=T["accent"],
                    selectcolor=T["accent_lt"],
                    cursor="hand2").pack(side=LEFT, padx=(0, 12))
    civil_status_var  = StringVar(value="SINGLE")
    fld(g1, "Civil Status", 1, 1, combo_var=civil_status_var,
        combo_vals=["SINGLE", "MARRIED", "WIDOWED", "DIVORCED"])
    nationality_entry = fld(g1, "Nationality",   1, 2)
    nationality_entry.insert(0, "FILIPINO")
    birth_date_entry  = fld(g1, "Birth Date",   2, 0, date=True)
    birth_place_entry = fld(g1, "Birth Place",  2, 1)
    age_entry          = fld(g1, "Age",             2, 2)


    g2 = section("Contact Information","#7c3aed")
    phone_entry       = fld(g2, "Phone Number",      0, 0)
    email_entry       = fld(g2, "Email Address",     0, 1)
    barangay_entry    = fld(g2, "Barangay",          0, 2)
    municipality_entry= fld(g2, "Municipality",      1, 0)
    province_entry    = fld(g2, "Province",          1, 1)
    province_entry.insert(0, "QUEZON")
    emergency_entry   = fld(g2, "Emergency Contact", 1, 2)

    g3 = section("ER Details", T["danger"])
    arrival_time_entry = fld(g3, "Arrival Time",            0, 0)
    arrival_time_entry.insert(0, datetime.now().strftime("%I:%M %p"))
    arrival_time_entry.config(fg=T["muted"])
    def on_focus_in(e):
        if arrival_time_entry.get() == datetime.now().strftime("%I:%M %p"):
            arrival_time_entry.delete(0, END)
            arrival_time_entry.config(fg=T["entry_fg"])
    def on_focus_out(e):
        if not arrival_time_entry.get().strip():
            arrival_time_entry.insert(0, datetime.now().strftime("%I:%M %p"))
            arrival_time_entry.config(fg=T["muted"])
    
    arrival_time_entry.bind("<FocusIn>", on_focus_in)
    arrival_time_entry.bind("<FocusOut>", on_focus_out)
    diagnosis_entry    = fld(g3, "Diagnosis",       0, 1, span=2)
    type_of_service_var = StringVar(value="MEDICINE")
    service_type_entry = fld(g3, "Type of Service", 1, 0, combo_var=type_of_service_var, combo_vals=["MEDICINE", "SURGICAL", "OB-GYNE", "PEDIATRICS", "OTHERS"])
    referred_to_entry  = fld(g3, "Referral To",     1, 1)
    seen_by_entry      = fld(g3, "Seen by Doctor",   1, 2)
    time_if_admit_entry= fld(g3, "Time if Admit",   2, 0)
    doctor_entry       = fld(g3, "Doctor",          2, 1)
    disposition_var = StringVar(value="")
    disposition_entry  = fld(g3, "Disposition",     2, 2, combo_var=disposition_var, combo_vals=["", "ADMITTED", "DISCHARGED", "REFERRED", "ABSCONDED", "TRANSFER", "DECEASED"])

    all_histories = load_all_history()

    barangay_history     = all_histories.get("barangay",     [])
    municipality_history = all_histories.get("municipality", [])
    province_history     = all_histories.get("province",     [])
    birth_place_history  = all_histories.get("birth_place",  [])
    nationality_history  = all_histories.get("nationality",  [])

    save_barangay     = add_input_history(barangay_entry,     barangay_history,     "barangay",     all_histories)
    save_municipality = add_input_history(municipality_entry, municipality_history, "municipality", all_histories)
    save_province     = add_input_history(province_entry,     province_history,     "province",     all_histories)
    save_birth_place  = add_input_history(birth_place_entry,  birth_place_history,  "birth_place",  all_histories)
    save_nationality  = add_input_history(nationality_entry,  nationality_history,  "nationality",  all_histories)

    def clear_patient_form():
        for w in [name_entry, middle_name_entry, last_name_entry,
                  phone_entry, email_entry, barangay_entry, municipality_entry,
                  province_entry, emergency_entry, arrival_time_entry, age_entry,
                  diagnosis_entry, service_type_entry, referred_to_entry,
                  seen_by_entry, time_if_admit_entry, doctor_entry]:
            w.delete(0, END)
        municipality_entry.insert(0, "CATANAUAN")
        province_entry.insert(0, "QUEZON")
        if hasattr(birth_date_entry, "set_date"):
            birth_date_entry.set_date(datetime.today())
        else:
            birth_date_entry.delete(0, END)
            civil_status_var.set("SINGLE")
            gender_var.set("MALE")
            nationality_entry.insert(0, "FILIPINO")
            birth_place_entry.insert(0, "CATANAUAN")

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
            "age":           age_entry.get().strip().upper(),
            "arrival_time":  arrival_time_entry.get().strip().upper(),
            "diagnosis":     diagnosis_entry.get().strip().upper(),
            "service_type":  service_type_entry.get().strip().upper(),
            "referred_to":   referred_to_entry.get().strip().upper(),
            "seen_by_doctor":seen_by_entry.get().strip().upper(),
            "disposition":   disposition_entry.get().strip().upper(),
            "time_if_admit": time_if_admit_entry.get().strip().upper(),
            "doctor":        doctor_entry.get().strip().upper(),
            "registered_by": (user_data.get("username") if user_data else "").upper(),
            "phone":         phone_entry.get().strip().upper(),
            "email":         email_entry.get().strip(),
            "barangay":      barangay_entry.get().strip().upper(),
            "municipality":  municipality_entry.get().strip().upper(),
            "province":      province_entry.get().strip().upper(),
            "medical_history": ""
        }
        er_data = dict(patient_data)
        er_data["case_number"] = case_number_label.cget("text")

        duplicate_patient_id = db.has_duplicate_patient(patient_data)

        if duplicate_patient_id and not force:
            messagebox.showwarning("Duplicate Patient",
                "A patient with the same name/birth date already exists.\n"
                "Use Save Anyway to save this ER visit separately without changing the existing patient.")
            return

        if duplicate_patient_id and force:
            if not messagebox.askyesno("Confirm", "Duplicate detected. Save anyway? This will create a separate ER visit for the existing patient."):
                return
            assigned_patient_id = duplicate_patient_id
            er_case_number = db.add_er_visit(duplicate_patient_id, er_data)
            if er_case_number:
                messagebox.showinfo("Registered",
                    f"ER visit saved for existing patient ID {duplicate_patient_id}.\nCase Number: {er_case_number}")
                patient_id_label.config(text=duplicate_patient_id)
                for key in ("patient_list", "dashboard"):
                    r = page_refreshers.get(key)
                    if r:
                        r()
                case_number_label.config(text=db.generate_next_case_number())
                clear_patient_form()
                return
            assigned_patient_id = None
        else:
            assigned_patient_id = db.add_patient(patient_data, include_case_number=False)
            if assigned_patient_id:
                er_case_number = db.add_er_visit(assigned_patient_id, er_data)
                if er_case_number:
                    messagebox.showinfo("Registered",
                        f"Patient {first_name} {last_name} registered.\nID: {assigned_patient_id}\nCase Number: {er_case_number}")
                else:
                    messagebox.showwarning(
                        "Partial Success",
                        f"Patient registered with ID {assigned_patient_id}, but saving the ER visit record failed."
                    )

        if assigned_patient_id:
            save_barangay    (barangay_entry.get())
            save_municipality(municipality_entry.get())
            save_province    (province_entry.get())
            save_birth_place (birth_place_entry.get())
            save_nationality (nationality_entry.get())

            patient_id_label.config(text=assigned_patient_id)
            for key in ("patient_list", "dashboard"):
                r = page_refreshers.get(key)
                if r:
                    r()
            case_number_label.config(text=db.generate_next_case_number())
            patient_id_label.config(text="Assign on save")
            clear_patient_form()
    
    bf = Frame(outer, bg=T["bg"])
    bf.pack(pady=(4, 20), anchor=W)
    mk_btn(bf, "Register Patient", register_patient, width=18).pack(side=LEFT, padx=(0, 8))
    mk_btn(bf, "Save Anyway", lambda: register_patient(force=True),
           color=T["warning"], width=14).pack(side=LEFT, padx=(0, 8))
    mk_btn(bf, "Clear Form", clear_patient_form, secondary=True, width=12).pack(side=LEFT)

    return frame