from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
from utils.theme import T, FONT
from utils.widgets import mk_entry, mk_btn, mk_combo, page_header, section_label
from utils.validators import (
    validate_age, validate_phone, validate_email, validate_date,
    uppercase_entry_widget, format_birthdate_entry
)
from models.patient_database import PatientDatabase

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None


def build_search_patient_page(parent, page_refreshers):
    """Build the patient search, view, and edit page."""
    outer = Frame(parent, bg=T["bg"])
    outer.rowconfigure(0, weight=1)
    outer.columnconfigure(0, weight=1)

    page_canvas = Canvas(outer, bg=T["bg"], highlightthickness=0)
    page_scroll = ttk.Scrollbar(outer, orient=VERTICAL, command=page_canvas.yview)
    page_canvas.configure(yscrollcommand=page_scroll.set)
    page_canvas.grid(row=0, column=0, sticky=NSEW)
    page_scroll.grid(row=0, column=1, sticky=NS)

    frame = Frame(page_canvas, bg=T["bg"])
    canvas_window = page_canvas.create_window((0, 0), window=frame, anchor="nw")

    def _on_frame_configure(event):
        page_canvas.configure(scrollregion=page_canvas.bbox("all"))
    def _on_canvas_configure(event):
        page_canvas.itemconfig(canvas_window, width=event.width)

    frame.bind("<Configure>", _on_frame_configure)
    page_canvas.bind("<Configure>", _on_canvas_configure)
    page_canvas.bind("<Enter>", lambda e: page_canvas.bind_all(
        "<MouseWheel>", lambda ev: page_canvas.yview_scroll(int(-1*(ev.delta/120)), "units")))
    page_canvas.bind("<Leave>", lambda e: page_canvas.unbind_all("<MouseWheel>"))

    frame.rowconfigure(3, weight=1)
    frame.columnconfigure(0, weight=1)
    db = PatientDatabase()
    selected_patient_id = StringVar(value="")

    page_header(frame, "Search Patient Records", "Find, view and edit patient records")

    # ── Search card ────────────────────────────────────────────
    sc = Frame(frame, bg=T["panel"],
               highlightthickness=1, highlightbackground=T["border"])
    sc.pack(fill=X, padx=24, pady=(14, 0))

    section_label(sc, "Search Filters")

    si = Frame(sc, bg=T["panel"])
    si.pack(fill=X, padx=20, pady=(0, 16))
    si.columnconfigure(0, weight=2)
    si.columnconfigure(1, weight=1)
    si.columnconfigure(2, weight=1)

    def sf(label, col):
        Label(si, text=label.upper(), font=FONT["tag"],
              bg=T["panel"], fg=T["muted"]).grid(
            row=0, column=col, sticky=W, pady=(0, 4),
            padx=(0 if col == 0 else 12, 8))
        e = mk_entry(si, width=24)
        e.grid(row=1, column=col, sticky=EW, ipady=8,
               padx=(0 if col == 0 else 12, 12))
        e.bind("<KeyRelease>", lambda ev: uppercase_entry_widget(e))
        e.bind("<Return>", lambda ev: search_patient())
        return e

    search_entry    = sf("ID or Full Name", 0)
    firstname_entry = sf("First Name", 1)
    lastname_entry  = sf("Last Name",  2)

    btn_row = Frame(sc, bg=T["panel"])
    btn_row.pack(anchor=W, padx=20, pady=(0, 14))
    mk_btn(btn_row, "Search", lambda: search_patient(), width=12).pack(side=LEFT, padx=(0, 8))
    mk_btn(btn_row, "Clear",  lambda: clear_search(), secondary=True, width=10).pack(side=LEFT)

    # ── Results table ──────────────────────────────────────────
    tbl_card = Frame(frame, bg=T["panel"],
                     highlightthickness=1, highlightbackground=T["border"])
    tbl_card.pack(fill=BOTH, expand=True, padx=24, pady=(10, 0))

    results_lbl = Label(tbl_card, text="RESULTS", font=FONT["tag"],
                        bg=T["panel"], fg=T["accent"])
    results_lbl.pack(anchor=W, padx=20, pady=(12, 2))
    Frame(tbl_card, bg=T["border"], height=1).pack(fill=X, padx=20, pady=(0, 6))

    rf = Frame(tbl_card, bg=T["panel"])
    rf.pack(fill=BOTH, expand=True, padx=16, pady=(0, 8))

    columns = ("ID", "Name", "Age", "Gender", "Birth Date", "Barangay", "Municipality", "Province", "Registered")
    results_tree = ttk.Treeview(rf, columns=columns, show="headings", height=7)
    for col in columns:
        results_tree.heading(col, text=col)
    results_tree.column("ID",            width=95,  anchor=W,      minwidth=70)
    results_tree.column("Name",          width=175, anchor=W,      minwidth=100)
    results_tree.column("Age",           width=50,  anchor=CENTER, minwidth=35)
    results_tree.column("Gender",        width=70,  anchor=CENTER, minwidth=50)
    results_tree.column("Birth Date",    width=95,  anchor=CENTER, minwidth=70)
    results_tree.column("Barangay",      width=120, anchor=W,      minwidth=80)
    results_tree.column("Municipality",  width=110, anchor=W,      minwidth=70)
    results_tree.column("Province",      width=110, anchor=W,      minwidth=70)
    results_tree.column("Registered",    width=130, anchor=W,      minwidth=80)
    results_tree.pack(fill=BOTH, expand=True)

    # ── Edit panel ────────────────────────────────────────────
    edit_card = Frame(frame, bg=T["panel"],
                      highlightthickness=1, highlightbackground=T["border"])
    edit_card.pack(fill=X, padx=24, pady=(10, 16))
    edit_card.columnconfigure(0, weight=1)

    section_label(edit_card, "Edit Selected Patient")

    edit_canvas = Canvas(edit_card, bg=T["panel"], highlightthickness=0, height=260)
    edit_sb = ttk.Scrollbar(edit_card, orient=VERTICAL, command=edit_canvas.yview)
    edit_sb.pack(side=RIGHT, fill=Y, padx=(0, 4), pady=(0, 8))
    edit_canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=(4, 0), pady=(0, 8))
    edit_canvas.configure(yscrollcommand=edit_sb.set)

    edit_frame = Frame(edit_canvas, bg=T["panel"])
    edit_frame_id = edit_canvas.create_window((0, 0), window=edit_frame, anchor="nw")

    def _edit_resize(e):
        edit_canvas.configure(scrollregion=edit_canvas.bbox("all"))
    def _edit_canvas_resize(e):
        edit_canvas.itemconfig(edit_frame_id, width=e.width)
    edit_frame.bind("<Configure>", _edit_resize)
    edit_canvas.bind("<Configure>", _edit_canvas_resize)
    edit_canvas.bind("<Enter>", lambda e: edit_canvas.bind_all(
        "<MouseWheel>", lambda ev: edit_canvas.yview_scroll(int(-1*(ev.delta/120)), "units")))
    edit_canvas.bind("<Leave>", lambda e: edit_canvas.unbind_all("<MouseWheel>"))

    for ci in (1, 3, 5, 7):
        edit_frame.columnconfigure(ci, weight=1)

    def ef(label, row, col=0, combo_var=None, combo_vals=None, readonly=False, date=False):
        Label(edit_frame, text=label.upper(), font=FONT["tag"],
              bg=T["panel"], fg=T["muted"]).grid(
            row=row*2, column=col, sticky=W, pady=(8, 3),
            padx=(0 if col == 0 else 14, 6))
        if combo_var and combo_vals:
            w = mk_combo(edit_frame, combo_var, combo_vals, width=18)
            w.grid(row=row*2+1, column=col, sticky=EW, ipady=5,
                   padx=(0 if col == 0 else 14, 14))
        elif date and DateEntry:
            w = DateEntry(edit_frame, width=18, date_pattern="yyyy-mm-dd", font=FONT["body"],
                          background=T["accent"], foreground=T["white"],
                          headersbackground=T["accent"])
            w.grid(row=row*2+1, column=col, sticky=EW,
                   padx=(0 if col == 0 else 14, 14))
        else:
            w = mk_entry(edit_frame, width=20, readonly=readonly)
            if readonly:
                w.config(textvariable=selected_patient_id)
            w.grid(row=row*2+1, column=col, sticky=EW, ipady=6,
                   padx=(0 if col == 0 else 14, 14))
            if not readonly and not date:
                w.bind("<KeyRelease>", lambda e, x=w: uppercase_entry_widget(x))
            if date and not DateEntry:
                w.bind("<KeyRelease>", lambda e, x=w: format_birthdate_entry(x))
        return w

    patient_id_entry     = ef("Patient ID",      0, 0, readonly=True)
    edit_first_name      = ef("First Name",      0, 2)
    edit_middle_name     = ef("Middle Name",     0, 4)
    edit_last_name       = ef("Last Name",       0, 6)
    edit_age             = ef("Age",             1, 0)
    edit_gender_var      = StringVar(value="MALE")
    ef("Gender",         1, 2, combo_var=edit_gender_var, combo_vals=["MALE", "FEMALE", "OTHER"])
    edit_birth_date      = ef("Birth Date",      1, 4, date=True)
    edit_birth_place     = ef("Birth Place",     1, 6)
    edit_civil_status_var = StringVar(value="SINGLE")
    ef("Civil Status",   2, 0, combo_var=edit_civil_status_var,
       combo_vals=["SINGLE", "MARRIED", "WIDOWED", "DIVORCED"])
    edit_nationality     = ef("Nationality",     2, 2)
    edit_phone           = ef("Phone",           2, 4)
    edit_email           = ef("Email",           2, 6)
    edit_barangay        = ef("Barangay",        3, 0)
    edit_municipality    = ef("Municipality",    3, 2)
    edit_municipality.insert(0, "CATANAUAN")
    edit_province        = ef("Province",        3, 4)
    edit_province.insert(0, "QUEZON")
    edit_medical_history = ef("Medical History", 4, 0)

    registered_by_label = Label(edit_frame, text="Registered By: N/A",
                                font=FONT["small"], bg=T["panel"], fg=T["muted"])
    registered_by_label.grid(row=8, column=0, columnspan=8, sticky=W, pady=(6, 0))

    def clear_edit_form():
        selected_patient_id.set("")
        for w in [edit_first_name, edit_middle_name, edit_last_name, edit_age,
                  edit_birth_place, edit_nationality, edit_phone, edit_email,
                  edit_barangay, edit_municipality, edit_province, edit_medical_history]:
            try:
                w.config(state="normal")
            except Exception:
                pass
            w.delete(0, END)
        edit_municipality.insert(0, "CATANAUAN")
        edit_province.insert(0, "QUEZON")
        edit_gender_var.set("MALE")
        if hasattr(edit_birth_date, "set_date"):
            edit_birth_date.set_date(datetime.today())
        else:
            edit_birth_date.delete(0, END)
        edit_civil_status_var.set("SINGLE")
        registered_by_label.config(text="Registered By: N/A")

    def load_results(patients):
        for item in results_tree.get_children():
            results_tree.delete(item)
        if not patients:
            results_tree.insert("", END, values=("No results found","","","","","","","",""))
            results_lbl.config(text="RESULTS  ·  0 records")
            return
        for i, (pid, pd) in enumerate(patients.items()):
            full_name = " ".join([pd.get("first_name",""), pd.get("middle_name",""),
                                  pd.get("last_name","")]).strip().upper() or "N/A"
            tag = "even" if i % 2 == 0 else "odd"
            results_tree.insert("", END, tags=(tag,), values=(
                pid, full_name,
                pd.get("age","N/A"),
                (pd.get("gender") or "N/A").upper(),
                pd.get("birth_date","N/A"),
                (pd.get("barangay") or "N/A").upper(),
                (pd.get("municipality") or "N/A").upper(),
                (pd.get("province") or "N/A").upper(),
                (pd.get("registered_by") or "N/A").upper()
            ))
        results_tree.tag_configure("even", background=T["row_even"])
        results_tree.tag_configure("odd",  background=T["row_odd"])
        results_lbl.config(text=f"RESULTS  ·  {len(patients)} record{'s' if len(patients) != 1 else ''}")

    def search_patient():
        search_term     = search_entry.get().strip().upper()
        first_name_term = firstname_entry.get().strip().upper()
        last_name_term  = lastname_entry.get().strip().upper()

        if not search_term and not first_name_term and not last_name_term:
            messagebox.showwarning("Warning", "Please enter a search term")
            return

        if first_name_term or last_name_term:
            combined = f"{first_name_term} {last_name_term}".strip()
            patients = db.search_patients(combined)
            if first_name_term and last_name_term:
                patients = {pid: p for pid, p in patients.items()
                            if first_name_term in (p.get("first_name") or "").upper()
                            and last_name_term in (p.get("last_name") or "").upper()}
            elif first_name_term:
                patients = {pid: p for pid, p in patients.items()
                            if first_name_term in (p.get("first_name") or "").upper()}
            else:
                patients = {pid: p for pid, p in patients.items()
                            if last_name_term in (p.get("last_name") or "").upper()}
            if search_term:
                patients.update(db.search_patients(search_term))
        else:
            patients = db.search_patients(search_term)

        load_results(patients)
        clear_edit_form()

    def clear_search():
        search_entry.delete(0, END)
        firstname_entry.delete(0, END)
        lastname_entry.delete(0, END)
        load_results({})
        clear_edit_form()
        results_lbl.config(text="RESULTS")

    def load_selected_patient(patient_data):
        clear_edit_form()
        selected_patient_id.set(patient_data.get("patient_id", ""))
        for w, key in [
            (edit_first_name,      "first_name"),
            (edit_middle_name,     "middle_name"),
            (edit_last_name,       "last_name"),
            (edit_age,             "age"),
            (edit_birth_place,     "birth_place"),
            (edit_phone,           "phone"),
            (edit_email,           "email"),
            (edit_barangay,        "barangay"),
            (edit_municipality,    "municipality"),
            (edit_province,        "province"),
            (edit_medical_history, "medical_history"),
            (edit_nationality,     "nationality"),
        ]:
            try:
                w.config(state="normal")
            except Exception:
                pass
            w.delete(0, END)
            w.insert(0, patient_data.get(key, "") or "")
        edit_gender_var.set((patient_data.get("gender") or "MALE").upper())
        edit_civil_status_var.set((patient_data.get("civil_status") or "SINGLE").upper())
        if hasattr(edit_birth_date, "set_date"):
            try:
                edit_birth_date.set_date(patient_data.get("birth_date") or datetime.today())
            except Exception:
                edit_birth_date.delete(0, END)
                edit_birth_date.insert(0, patient_data.get("birth_date", "") or "")
        else:
            edit_birth_date.delete(0, END)
            edit_birth_date.insert(0, patient_data.get("birth_date", "") or "")
        registered_by_label.config(
            text=f"Registered By: {(patient_data.get('registered_by') or 'N/A').upper()}")

    def on_tree_select(event):
        sel = results_tree.selection()
        if not sel:
            return
        item = results_tree.item(sel)
        pid = item["values"][0]
        if pid == "No results found":
            return
        pd2 = db.get_patient(pid)
        if pd2:
            load_selected_patient(pd2)

    def open_update_popup():
        pid = selected_patient_id.get()
        if not pid:
            messagebox.showwarning("Warning", "Select a patient record before updating")
            return
        patient_data = db.get_patient(pid)
        if not patient_data:
            messagebox.showerror("Error", "Unable to load selected patient record")
            return

        popup = Toplevel(frame)
        popup.title(f"Update Patient {pid}")
        popup.configure(bg=T["bg"])
        popup.transient(frame.winfo_toplevel())
        popup.grab_set()
        popup.minsize(760, 520)
        
        # Center the popup window
        popup.update_idletasks()
        width, height = 760, 520
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'{width}x{height}+{x}+{y}')

        header = Frame(popup, bg=T["bg"])
        header.pack(fill=X, padx=16, pady=(12, 6))
        Label(header, text=f"Update Patient {pid}", font=("Arial", 16, "bold"),
              bg=T["bg"], fg=T["text"]).pack(anchor=W)
        Label(header, text="Edit patient details in a dedicated popup window.",
              font=FONT["small"], bg=T["bg"], fg=T["muted"]).pack(anchor=W, pady=(2, 0))

        body = Frame(popup, bg=T["panel"], highlightthickness=1,
                     highlightbackground=T["border"])
        body.pack(fill=BOTH, expand=True, padx=16, pady=(0, 12))
        for ci in (0, 2, 4, 6):
            body.columnconfigure(ci, weight=1)

        def pf(label, row, col=0, combo_var=None, combo_vals=None, date=False):
            Label(body, text=label.upper(), font=FONT["tag"], bg=T["panel"],
                  fg=T["muted"]).grid(row=row*2, column=col, sticky=W,
                                      pady=(10, 4), padx=(0 if col == 0 else 12, 6))
            if combo_var and combo_vals:
                w = mk_combo(body, combo_var, combo_vals, width=20)
                w.grid(row=row*2+1, column=col, sticky=EW, ipady=5,
                       padx=(0 if col == 0 else 12, 12))
            elif date and DateEntry:
                w = DateEntry(body, width=20, date_pattern="yyyy-mm-dd", font=FONT["body"],
                              background=T["accent"], foreground=T["white"],
                              headersbackground=T["accent"])
                w.grid(row=row*2+1, column=col, sticky=EW,
                       padx=(0 if col == 0 else 12, 12), pady=(0, 2))
            else:
                w = mk_entry(body, width=20)
                w.grid(row=row*2+1, column=col, sticky=EW, ipady=6,
                       padx=(0 if col == 0 else 12, 12), pady=(0, 2))
                w.bind("<KeyRelease>", lambda e, x=w: uppercase_entry_widget(x))
            return w

        popup_first_name       = pf("First Name",      0, 0)
        popup_middle_name      = pf("Middle Name",     0, 2)
        popup_last_name        = pf("Last Name",       0, 4)
        popup_age              = pf("Age",             1, 0)
        popup_gender_var       = StringVar(value=(patient_data.get("gender") or "MALE").upper())
        pf("Gender",           1, 2, combo_var=popup_gender_var,
           combo_vals=["MALE", "FEMALE", "OTHER"])
        popup_birth_date       = pf("Birth Date",      1, 4, date=True)
        popup_birth_place      = pf("Birth Place",     1, 6)
        popup_civil_status_var = StringVar(value=(patient_data.get("civil_status") or "SINGLE").upper())
        pf("Civil Status",     2, 0, combo_var=popup_civil_status_var,
           combo_vals=["SINGLE", "MARRIED", "WIDOWED", "DIVORCED"])
        popup_nationality      = pf("Nationality",     2, 2)
        popup_phone            = pf("Phone",           2, 4)
        popup_email            = pf("Email",           2, 6)
        popup_barangay         = pf("Barangay",        3, 0)
        popup_municipality     = pf("Municipality",    3, 2)
        popup_municipality.insert(0, "CATANAUAN")
        popup_province         = pf("Province",        3, 4)
        popup_province.insert(0, "QUEZON")
        popup_medical_history  = pf("Medical History", 4, 0)

        def populate_popup():
            for w, key in [
                (popup_first_name,      "first_name"),
                (popup_middle_name,     "middle_name"),
                (popup_last_name,       "last_name"),
                (popup_age,             "age"),
                (popup_birth_place,     "birth_place"),
                (popup_nationality,     "nationality"),
                (popup_phone,           "phone"),
                (popup_email,           "email"),
                (popup_barangay,        "barangay"),
                (popup_municipality,    "municipality"),
                (popup_province,        "province"),
                (popup_medical_history, "medical_history"),
            ]:
                w.delete(0, END)
                w.insert(0, patient_data.get(key, "") or "")
            if hasattr(popup_birth_date, "set_date"):
                try:
                    popup_birth_date.set_date(patient_data.get("birth_date") or datetime.today())
                except Exception:
                    popup_birth_date.delete(0, END)
                    popup_birth_date.insert(0, patient_data.get("birth_date", "") or "")
            else:
                popup_birth_date.delete(0, END)
                popup_birth_date.insert(0, patient_data.get("birth_date", "") or "")

        populate_popup()

        def save_popup_changes():
            if not popup_first_name.get().strip() or not popup_last_name.get().strip():
                messagebox.showerror("Error", "First Name and Last Name are required", parent=popup)
                return
            if not validate_age(popup_age.get()):
                messagebox.showerror("Error", "Please enter a valid age (1-149)", parent=popup)
                return
            if popup_phone.get().strip() and not validate_phone(popup_phone.get()):
                messagebox.showerror("Error", "Please enter a valid phone number", parent=popup)
                return
            if popup_email.get().strip() and not validate_email(popup_email.get()):
                messagebox.showerror("Error", "Please enter a valid email address", parent=popup)
                return
            bv = popup_birth_date.get().strip()
            if bv and not validate_date(bv):
                messagebox.showerror("Error", "Please enter a valid birth date in YYYY-MM-DD format", parent=popup)
                return

            updated_data = {
                "first_name":      popup_first_name.get().strip().upper(),
                "middle_name":     popup_middle_name.get().strip().upper(),
                "last_name":       popup_last_name.get().strip().upper(),
                "age":             popup_age.get().strip(),
                "gender":          popup_gender_var.get().upper(),
                "birth_date":      bv or None,
                "birth_place":     popup_birth_place.get().strip().upper(),
                "civil_status":    popup_civil_status_var.get().upper(),
                "nationality":     popup_nationality.get().strip().upper(),
                "phone":           popup_phone.get().strip().upper(),
                "email":           popup_email.get().strip().upper(),
                "barangay":        popup_barangay.get().strip().upper(),
                "municipality":    popup_municipality.get().strip().upper(),
                "province":        popup_province.get().strip().upper(),
                "medical_history": popup_medical_history.get().strip().upper()
            }

            if db.update_patient(pid, updated_data):
                messagebox.showinfo("Success", f"Patient {pid} updated successfully", parent=popup)
                load_selected_patient(db.get_patient(pid))
                if search_entry.get().strip():
                    search_patient()
                else:
                    load_results({})
                for key in ("patient_list", "dashboard"):
                    r = page_refreshers.get(key)
                    if r:
                        r()
                popup.destroy()
            else:
                messagebox.showerror("Error", "Unable to update patient record", parent=popup)

        btn_row = Frame(popup, bg=T["bg"])
        btn_row.pack(fill=X, padx=16, pady=(0, 16))
        mk_btn(btn_row, "Save Changes", save_popup_changes, width=16).pack(side=LEFT, padx=(0, 8))
        mk_btn(btn_row, "Cancel", popup.destroy, secondary=True, width=12).pack(side=LEFT)

    def delete_patient():
        pid = selected_patient_id.get()
        if not pid:
            messagebox.showwarning("Warning", "Select a patient record before deleting")
            return
        if not messagebox.askyesno("Confirm Delete",
                f"Delete patient record {pid}?\nThis cannot be undone."):
            return
        if db.delete_patient(pid):
            messagebox.showinfo("Deleted", f"Patient {pid} deleted successfully")
            clear_edit_form()
            if search_entry.get().strip():
                search_patient()
            else:
                load_results({})
            for key in ("patient_list", "dashboard"):
                r = page_refreshers.get(key)
                if r:
                    r()
        else:
            messagebox.showerror("Error", "Unable to delete patient record")

    results_tree.bind("<<TreeviewSelect>>", on_tree_select)

    af = Frame(edit_card, bg=T["panel"])
    af.pack(fill=X, padx=20, pady=(0, 16))
    mk_btn(af, "Update Record", open_update_popup, width=16).pack(side=LEFT, padx=(0, 8))
    mk_btn(af, "Delete Record", delete_patient, danger=True, width=14).pack(side=LEFT, padx=(0, 8))
    mk_btn(af, "Clear Form",    clear_edit_form, secondary=True, width=12).pack(side=LEFT)

    load_results({})
    return outer
