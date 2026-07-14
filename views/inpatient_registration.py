import os
import sys
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.theme import T, FONT
from utils.widgets import mk_entry, mk_btn, mk_combo, section_label
from models.patient_database import PatientDatabase
from models.visit_database import VisitDatabase


def build_inpatient_registration_page(parent, user_data, page_refreshers):
    """In-Patient registration — search patient, admit, discharge."""

    db_pat  = PatientDatabase()
    db_vis  = VisitDatabase()

    # ── Root frame ─────────────────────────────────────────
    frame = Frame(parent, bg=T["bg"])
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # ── Page header ────────────────────────────────────────
    header = Frame(frame, bg=T["panel"])
    header.grid(row=0, column=0, columnspan=2, sticky=EW)
    Frame(header, bg="#7c3aed", height=3).pack(fill=X)
    hinner = Frame(header, bg=T["panel"])
    hinner.pack(fill=X, padx=28, pady=(14, 12))
    Label(hinner, text="In-Patient Registration",
          font=FONT["h1"], bg=T["panel"], fg=T["text"]).pack(anchor=W)
    Label(hinner, text="Admit patients, manage wards, and process discharges",
          font=FONT["body"], bg=T["panel"], fg=T["muted"]).pack(anchor=W, pady=(2, 0))
    Frame(header, bg=T["border"], height=1).pack(fill=X)

    # ── Scrollable canvas ──────────────────────────────────
    canvas = Canvas(frame, bg=T["bg"], highlightthickness=0)
    vsb    = ttk.Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.grid   (row=1, column=1, sticky=NS)
    canvas.grid(row=1, column=0, sticky=NSEW)

    cf = Frame(canvas, bg=T["bg"])
    cw = canvas.create_window((0, 0), window=cf, anchor="nw")

    cf.bind("<Configure>",     lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=canvas.winfo_width()))
    canvas.bind("<Enter>",     lambda e: canvas.bind_all("<MouseWheel>",
        lambda ev: canvas.yview_scroll(int(-1*(ev.delta/120)), "units")))
    canvas.bind("<Leave>",     lambda e: canvas.unbind_all("<MouseWheel>"))

    outer = Frame(cf, bg=T["bg"])
    outer.pack(fill=BOTH, expand=True, padx=24, pady=16)
    outer.columnconfigure(0, weight=1)

    # ── SECTION 1 — Search patient ─────────────────────────
    search_card = Frame(outer, bg=T["panel"],
                        highlightthickness=1, highlightbackground=T["border"])
    search_card.pack(fill=X, pady=(0, 12))
    Frame(search_card, bg="#7c3aed", height=2).pack(fill=X)
    Label(search_card, text="FIND PATIENT", font=FONT["tag"],
          bg=T["panel"], fg="#7c3aed").pack(anchor=W, padx=20, pady=(10, 2))
    Frame(search_card, bg=T["border"], height=1).pack(fill=X, padx=20, pady=(0, 8))

    sf = Frame(search_card, bg=T["panel"])
    sf.pack(fill=X, padx=20, pady=(0, 14))
    sf.columnconfigure(0, weight=2)
    sf.columnconfigure(1, weight=1)
    sf.columnconfigure(2, weight=1)

    def sf_label(text, col):
        Label(sf, text=text, font=FONT["tag"],
              bg=T["panel"], fg=T["muted"]).grid(
            row=0, column=col, sticky=W, pady=(0, 4),
            padx=(0 if col == 0 else 12, 8))
        e = mk_entry(sf, width=22)
        e.grid(row=1, column=col, sticky=EW, ipady=8,
               padx=(0 if col == 0 else 12, 12))
        e.bind("<Return>", lambda ev: search_patient())
        return e

    search_entry    = sf_label("ID OR FULL NAME", 0)
    firstname_entry = sf_label("FIRST NAME",      1)
    lastname_entry  = sf_label("LAST NAME",       2)

    btn_row = Frame(search_card, bg=T["panel"])
    btn_row.pack(anchor=W, padx=20, pady=(0, 14))
    mk_btn(btn_row, "Search Patient", lambda: search_patient(),
           width=16).pack(side=LEFT, padx=(0, 8))
    mk_btn(btn_row, "Clear", lambda: clear_search(),
           secondary=True, width=10).pack(side=LEFT)

    # Search results
    results_lbl = Label(search_card, text="SEARCH RESULTS",
                        font=FONT["tag"], bg=T["panel"], fg=T["accent"])
    results_lbl.pack(anchor=W, padx=20, pady=(0, 4))
    Frame(search_card, bg=T["border"], height=1).pack(fill=X, padx=20, pady=(0, 6))

    rf = Frame(search_card, bg=T["panel"])
    rf.pack(fill=X, padx=20, pady=(0, 14))

    s_cols = ("Patient ID", "Name", "Gender", "Birth Date", "Phone", "Barangay")
    search_tree = ttk.Treeview(rf, columns=s_cols, show="headings", height=5)
    for col in s_cols:
        search_tree.heading(col, text=col)
    search_tree.column("Patient ID",  width=100, anchor=CENTER)
    search_tree.column("Name",        width=200, anchor=W)
    search_tree.column("Gender",      width=70,  anchor=CENTER)
    search_tree.column("Birth Date",  width=110, anchor=CENTER)
    search_tree.column("Phone",       width=120, anchor=W)
    search_tree.column("Barangay",    width=140, anchor=W)
    ssb = ttk.Scrollbar(rf, orient=VERTICAL, command=search_tree.yview)
    search_tree.configure(yscrollcommand=ssb.set)
    search_tree.pack(side=LEFT, fill=X, expand=True)
    ssb.pack(side=RIGHT, fill=Y)

    selected_pid = StringVar(value="")

    # ── SECTION 2 — Admit form ─────────────────────────────
    admit_card = Frame(outer, bg=T["panel"],
                       highlightthickness=1, highlightbackground=T["border"])
    admit_card.pack(fill=X, pady=(0, 12))
    Frame(admit_card, bg="#7c3aed", height=2).pack(fill=X)
    Label(admit_card, text="ADMISSION DETAILS", font=FONT["tag"],
          bg=T["panel"], fg="#7c3aed").pack(anchor=W, padx=20, pady=(10, 2))
    Frame(admit_card, bg=T["border"], height=1).pack(fill=X, padx=20, pady=(0, 8))

    # Selected patient badge
    sel_frame = Frame(admit_card, bg=T["accent_lt"],
                      highlightthickness=1, highlightbackground=T["accent"])
    sel_frame.pack(fill=X, padx=20, pady=(0, 12))
    Label(sel_frame, text="SELECTED PATIENT", font=FONT["tag"],
          bg=T["accent_lt"], fg=T["accent"], padx=12, pady=4).pack(side=LEFT)
    selected_name_lbl = Label(sel_frame, text="— none selected —",
                              font=FONT["body_b"], bg=T["accent_lt"],
                              fg=T["text"], padx=12, pady=4)
    selected_name_lbl.pack(side=LEFT)
    selected_id_lbl = Label(sel_frame, text="",
                            font=FONT["mono"], bg=T["accent_lt"],
                            fg=T["accent"], padx=8, pady=4)
    selected_id_lbl.pack(side=RIGHT, padx=12)

    ag = Frame(admit_card, bg=T["panel"])
    ag.pack(fill=X, padx=20, pady=(0, 16))
    for i in range(3):
        ag.columnconfigure(i, weight=1)

    def af(label, row, col, combo_var=None, combo_vals=None, span=1):
        px = 0 if col == 0 else 16
        Label(ag, text=label, font=FONT["tag"],
              bg=T["panel"], fg=T["muted"]).grid(
            row=row*2, column=col, columnspan=span,
            sticky=W, pady=(10, 3), padx=(px, 8))
        if combo_var and combo_vals:
            w = mk_combo(ag, combo_var, combo_vals, width=22)
            w.grid(row=row*2+1, column=col, columnspan=span,
                   sticky=EW, ipady=6, padx=(px, 16))
        else:
            w = mk_entry(ag, width=22)
            w.grid(row=row*2+1, column=col, columnspan=span,
                   sticky=EW, ipady=8, padx=(px, 16))
        return w

    diagnosis_entry    = af("DIAGNOSIS",          0, 0, span=3)
    ward_var           = StringVar(value="")
    af("WARD",                1, 0, combo_var=ward_var,
       combo_vals=["STATION 1", "STATION 2", "OB-GYNE", "EMERGENCY ROOM",
                   "ICU", "PRIVATE", "CHARITY"])
    room_entry         = af("ROOM NO.",           1, 1)
    bed_entry          = af("BED NO.",            1, 2)
    doctor_entry       = af("ATTENDING DOCTOR",   2, 0)
    service_type_var   = StringVar(value="")
    af("SERVICE TYPE",        2, 1, combo_var=service_type_var,
       combo_vals=["MEDICINE", "SURGICAL", "OB-GYNE", "PEDIATRICS", "OTHERS"])
    referred_entry     = af("REFERRED FROM",      2, 2)
    remarks_entry      = af("INITIAL REMARKS",    3, 0, span=3)

    # Re-layout diagnosis to span full width
    diagnosis_entry.grid(row=1, column=0, columnspan=3,
                         sticky=EW, ipady=8, padx=(0, 16))

    def clear_admit_form():
        for w in [room_entry, bed_entry, doctor_entry,
                  referred_entry, remarks_entry, diagnosis_entry]:
            w.delete(0, END)
        ward_var.set("")
        service_type_var.set("")

    def admit_patient():
        pid = selected_pid.get()
        if not pid:
            messagebox.showwarning("No Patient Selected",
                "Please search and select a patient before admitting.")
            return
        if not ward_var.get():
            messagebox.showerror("Error", "Please select a ward.")
            return
        if not doctor_entry.get().strip():
            messagebox.showerror("Error", "Attending Doctor is required.")
            return

        visit_data = {
            "patient_id":    pid,
            "visit_type":    "IPD",
            "diagnosis":     diagnosis_entry.get().strip().upper(),
            "service_type":  service_type_var.get().upper(),
            "referred_to":   referred_entry.get().strip().upper(),
            "doctor":        doctor_entry.get().strip().upper(),
            "registered_by": (user_data.get("username") or "").upper(),
        }
        visit_no = db_vis.add_visit(visit_data)
        if not visit_no:
            messagebox.showerror("Error", "Failed to create visit record.")
            return

        visit_id = db_vis.get_visit_id(visit_no)
        if not visit_id:
            messagebox.showerror("Error", "Could not retrieve visit ID.")
            return

        admission_data = {
            "patient_id":       pid,
            "ward":             ward_var.get().upper(),
            "room_no":          room_entry.get().strip().upper(),
            "bed_no":           bed_entry.get().strip().upper(),
            "attending_doctor": doctor_entry.get().strip().upper(),
            "remarks":          remarks_entry.get().strip().upper(),
        }
        if db_vis.add_admission(visit_id, admission_data):
            pname = selected_name_lbl.cget("text")
            messagebox.showinfo("Admitted",
                f"Patient admitted successfully.\n\n"
                f"Name:     {pname}\n"
                f"Visit No: {visit_no}\n"
                f"Ward:     {ward_var.get()}\n"
                f"Room:     {room_entry.get() or '—'} / Bed: {bed_entry.get() or '—'}")
            clear_admit_form()
            selected_pid.set("")
            selected_name_lbl.config(text="— none selected —")
            selected_id_lbl.config(text="")
            load_admitted()
            r = page_refreshers.get("dashboard")
            if r:
                r()
        else:
            messagebox.showerror("Error", "Failed to save admission record.")

    bf = Frame(admit_card, bg=T["panel"])
    bf.pack(anchor=W, padx=20, pady=(0, 16))
    mk_btn(bf, "Admit Patient", admit_patient,
           color="#7c3aed", width=16).pack(side=LEFT, padx=(0, 8))
    mk_btn(bf, "Clear", clear_admit_form,
           secondary=True, width=10).pack(side=LEFT)

    # ── SECTION 3 — Currently admitted ────────────────────
    admitted_card = Frame(outer, bg=T["panel"],
                          highlightthickness=1, highlightbackground=T["border"])
    admitted_card.pack(fill=BOTH, expand=True, pady=(0, 8))
    Frame(admitted_card, bg=T["success"], height=2).pack(fill=X)

    admitted_header = Frame(admitted_card, bg=T["panel"])
    admitted_header.pack(fill=X, padx=20, pady=(10, 2))
    admitted_lbl = Label(admitted_header, text="CURRENTLY ADMITTED PATIENTS",
                         font=FONT["tag"], bg=T["panel"], fg=T["success"])
    admitted_lbl.pack(side=LEFT)

    Frame(admitted_card, bg=T["border"], height=1).pack(fill=X, padx=20, pady=(0, 8))

    atf = Frame(admitted_card, bg=T["panel"])
    atf.pack(fill=BOTH, expand=True, padx=20, pady=(0, 14))

    a_cols = ("Admission ID", "Patient ID", "Name", "Ward",
              "Room", "Bed", "Doctor", "Diagnosis", "Admitted On")
    admitted_tree = ttk.Treeview(atf, columns=a_cols, show="headings", height=10)
    for col in a_cols:
        admitted_tree.heading(col, text=col)
    admitted_tree.column("Admission ID", width=100, anchor=CENTER)
    admitted_tree.column("Patient ID",   width=90,  anchor=CENTER)
    admitted_tree.column("Name",         width=180, anchor=W)
    admitted_tree.column("Ward",         width=90,  anchor=CENTER)
    admitted_tree.column("Room",         width=60,  anchor=CENTER)
    admitted_tree.column("Bed",          width=55,  anchor=CENTER)
    admitted_tree.column("Doctor",       width=140, anchor=W)
    admitted_tree.column("Diagnosis",    width=180, anchor=W)
    admitted_tree.column("Admitted On",  width=160, anchor=CENTER)

    asb = ttk.Scrollbar(atf, orient=VERTICAL, command=admitted_tree.yview)
    admitted_tree.configure(yscrollcommand=asb.set)
    admitted_tree.pack(side=LEFT, fill=BOTH, expand=True)
    asb.pack(side=RIGHT, fill=Y)

    admitted_tree.tag_configure("even", background=T["row_even"])
    admitted_tree.tag_configure("odd",  background=T["row_odd"])

    def load_admitted():
        for item in admitted_tree.get_children():
            admitted_tree.delete(item)
        admissions = db_vis.get_admitted_patients()
        count = len(admissions)
        admitted_lbl.config(
            text=f"CURRENTLY ADMITTED PATIENTS  ·  {count} patient{'s' if count != 1 else ''}")
        for i, (aid, a) in enumerate(admissions.items()):
            full = " ".join(filter(None, [
                a.get("first_name"), a.get("middle_name"), a.get("last_name")
            ])).title()
            tag = "even" if i % 2 == 0 else "odd"
            admitted_tree.insert("", END, tags=(tag,), values=(
                aid,
                a.get("patient_id", ""),
                full or "N/A",
                a.get("ward", ""),
                a.get("room_no", "—"),
                a.get("bed_no",  "—"),
                a.get("attending_doctor", ""),
                a.get("diagnosis", ""),
                a.get("admission_date", ""),
            ))

    # ── Discharge popup ────────────────────────────────────
    def open_discharge_popup():
        sel = admitted_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection",
                "Select a patient from the admitted list to discharge.")
            return
        item   = admitted_tree.item(sel)
        values = item["values"]
        aid    = values[0]
        pid    = values[1]
        pname  = values[2]
        ward   = values[3]

        popup = Toplevel(frame)
        popup.title(f"Discharge Patient — {pname}")
        popup.configure(bg=T["bg"])
        popup.transient(frame.winfo_toplevel())
        popup.grab_set()
        popup.resizable(False, False)

        Frame(popup, bg=T["danger"], height=3).pack(fill=X)
        hf = Frame(popup, bg=T["bg"])
        hf.pack(fill=X, padx=20, pady=(14, 6))
        Label(hf, text="Discharge Patient",
              font=FONT["h2"], bg=T["bg"], fg=T["text"]).pack(anchor=W)
        Label(hf, text=f"{pname}  ·  ID: {pid}  ·  Ward: {ward}",
              font=FONT["body"], bg=T["bg"], fg=T["muted"]).pack(anchor=W, pady=(2, 0))

        body = Frame(popup, bg=T["panel"],
                     highlightthickness=1, highlightbackground=T["border"])
        body.pack(fill=X, padx=20, pady=(0, 12))

        Label(body, text="DISCHARGE REMARKS / NOTES", font=FONT["tag"],
              bg=T["panel"], fg=T["muted"]).pack(anchor=W, padx=16, pady=(12, 4))
        remarks_var = mk_entry(body, width=50)
        remarks_var.pack(fill=X, padx=16, ipady=8, pady=(0, 16))

        Label(body, text="Time of Discharged Doctor's Order", font=FONT["tag"],
              bg=T["panel"], fg=T["muted"]).pack(anchor=W, padx=16, pady=(0, 4))
        discharge_time_var = mk_entry(body, width=50)
        discharge_time_var.pack(fill=X, padx=16, ipady=8, pady=(0, 16))

        def confirm_discharge():
            remarks = remarks_var.get().strip().upper()
            time_of_discharged_dr_order = discharge_time_var.get().strip()
            if not messagebox.askyesno("Confirm Discharge",
                    f"Discharge {pname}?\n\nThis will set the status to DISCHARGED."):
                return
            if db_vis.discharge_patient(aid, remarks, time_of_discharged_dr_order):
                messagebox.showinfo("Discharged",
                    f"{pname} has been discharged successfully.")
                popup.destroy()
                load_admitted()
                r = page_refreshers.get("dashboard")
                if r:
                    r()
            else:
                messagebox.showerror("Error", "Failed to process discharge.")

        bf2 = Frame(popup, bg=T["bg"])
        bf2.pack(padx=20, pady=(0, 16), anchor=W)
        mk_btn(bf2, "Confirm Discharge", confirm_discharge,
               danger=True, width=18).pack(side=LEFT, padx=(0, 8))
        mk_btn(bf2, "Cancel", popup.destroy,
               secondary=True, width=10).pack(side=LEFT)

    db_row = Frame(admitted_card, bg=T["panel"])
    db_row.pack(anchor=W, padx=20, pady=(0, 14))
    mk_btn(db_row, "Discharge Selected", open_discharge_popup,
           danger=True, width=18).pack(side=LEFT, padx=(0, 8))
    mk_btn(db_row, "⟳  Refresh", load_admitted,
           secondary=True, width=12).pack(side=LEFT)

    # ── Search helpers ─────────────────────────────────────
    def search_patient():
        term  = search_entry.get().strip().upper()
        fname = firstname_entry.get().strip().upper()
        lname = lastname_entry.get().strip().upper()
        if not term and not fname and not lname:
            messagebox.showwarning("Warning", "Enter a search term.")
            return
        combined = term or f"{fname} {lname}".strip()
        patients = db_pat.search_patients(combined)
        if fname and lname:
            patients = {pid: p for pid, p in patients.items()
                        if fname in (p.get("first_name") or "").upper()
                        and lname in (p.get("last_name") or "").upper()}

        for item in search_tree.get_children():
            search_tree.delete(item)
        if not patients:
            search_tree.insert("", END, values=("No results","","","","",""))
            results_lbl.config(text="SEARCH RESULTS  ·  0 records")
            return
        for i, (pid, p) in enumerate(patients.items()):
            full = " ".join(filter(None, [
                p.get("first_name"), p.get("middle_name"), p.get("last_name")
            ])).title()
            tag = "even" if i % 2 == 0 else "odd"
            search_tree.insert("", END, tags=(tag,), values=(
                pid, full,
                (p.get("gender") or "").title(),
                p.get("birth_date") or "",
                p.get("phone") or "",
                p.get("barangay") or "",
            ))
        search_tree.tag_configure("even", background=T["row_even"])
        search_tree.tag_configure("odd",  background=T["row_odd"])
        results_lbl.config(
            text=f"SEARCH RESULTS  ·  {len(patients)} record{'s' if len(patients)!=1 else ''}")

    def on_search_select(event):
        sel = search_tree.selection()
        if not sel:
            return
        values = search_tree.item(sel)["values"]
        pid    = str(values[0])
        pname  = str(values[1])
        if pid == "No results":
            return
        selected_pid.set(pid)
        selected_name_lbl.config(text=pname)
        selected_id_lbl.config(text=f"ID: {pid}")

    def clear_search():
        search_entry.delete(0, END)
        firstname_entry.delete(0, END)
        lastname_entry.delete(0, END)
        for item in search_tree.get_children():
            search_tree.delete(item)
        results_lbl.config(text="SEARCH RESULTS")
        selected_pid.set("")
        selected_name_lbl.config(text="— none selected —")
        selected_id_lbl.config(text="")

    search_tree.bind("<<TreeviewSelect>>", on_search_select)

    # Register refresher
    page_refreshers["inpatient"] = lambda: load_admitted()

    load_admitted()
    return frame
