import os
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from models.patient_database import PatientDatabase
from utils.theme import T, FONT
from utils.widgets import mk_entry, mk_combo, page_header
from utils.validators import validate_date

try:
    import openpyxl
    from openpyxl.workbook import Workbook
except ImportError:
    openpyxl = None


def build_er_report_page(parent, page_refreshers=None):
    frame = Frame(parent, bg=T["bg"])
    page_header(frame, "ER Patient Report", "Export ER patient registration data to Excel")

    db = PatientDatabase()

    content = Frame(frame, bg=T["bg"])
    content.pack(fill=BOTH, expand=True, padx=24, pady=16)

    def _normalize_report_date(date_text):
        for fmt in ["%m-%d-%Y", "%m/%d/%Y", "%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"]:
            try:
                return datetime.strptime(date_text, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    filter_card = Frame(content, bg=T["panel"], highlightthickness=1, highlightbackground=T["border"])
    filter_card.pack(fill=X, pady=(0, 18))
    filter_body = Frame(filter_card, bg=T["panel"])
    filter_body.pack(fill=X, padx=20, pady=16)

    Label(filter_body, text="Export Filter", font=FONT["tag"], bg=T["panel"], fg=T["accent"]).grid(row=0, column=0, columnspan=4, sticky=W)
    Label(filter_body, text="ER Records Only", font=FONT["tag"], bg=T["panel"], fg=T["muted"]).grid(row=1, column=0, sticky=W, pady=(12, 4))
    Label(filter_body, text="This report exports only ER-registered patients.", font=FONT["body"], bg=T["panel"], fg=T["text"]).grid(row=2, column=0, columnspan=3, sticky=W, pady=(0, 12))

    Label(filter_body, text="Start Date", font=FONT["tag"], bg=T["panel"], fg=T["muted"]).grid(row=3, column=0, sticky=W, pady=(12, 4))
    from_date_entry = mk_entry(filter_body, width=18)
    from_date_entry.grid(row=4, column=0, sticky=W)
    Label(filter_body, text="End Date", font=FONT["tag"], bg=T["panel"], fg=T["muted"]).grid(row=3, column=1, sticky=W, pady=(12, 4), padx=(24, 0))
    to_date_entry = mk_entry(filter_body, width=18)
    to_date_entry.grid(row=4, column=1, sticky=W, padx=(24, 0))
    Label(filter_body, text="Date format: MM-DD-YYYY or YYYY-MM-DD", font=FONT["small"], bg=T["panel"], fg=T["muted"]).grid(row=5, column=0, columnspan=3, sticky=W, pady=(8, 0))

    if openpyxl is None:
        Label(content, text="Missing dependency: openpyxl is required for Excel export.",
              font=FONT["body"], bg=T["bg"], fg=T["danger"]).pack(anchor=W, pady=(0, 12))
        Label(content, text="Install with: pip install openpyxl",
              font=FONT["body"], bg=T["bg"], fg=T["muted"]).pack(anchor=W)
        return frame

    def export_to_excel():
        start_date_raw = from_date_entry.get().strip()
        end_date_raw = to_date_entry.get().strip()

        start_date = None
        end_date = None
        if start_date_raw:
            if not validate_date(start_date_raw):
                messagebox.showerror("Invalid date", "Start date must be in MM-DD-YYYY or YYYY-MM-DD format.")
                return
            start_date = _normalize_report_date(start_date_raw)
        if end_date_raw:
            if not validate_date(end_date_raw):
                messagebox.showerror("Invalid date", "End date must be in MM-DD-YYYY or YYYY-MM-DD format.")
                return
            end_date = _normalize_report_date(end_date_raw)
        if start_date and end_date and start_date > end_date:
            messagebox.showerror("Invalid date range", "Start date cannot be after end date.")
            return

        patients = db.get_patients(
            er_only=True,
            start_date=start_date,
            end_date=end_date
        )

        if not patients:
            messagebox.showinfo("No Data", "There are no patient records to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            title="Save ER Patient Report"
        )
        if not file_path:
            return

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "ER Patient Report"

            headers = [
                "Case Number", "Patient ID", "Arrival Time", "First Name", "Middle Name", "Last Name",
                "Barangay", "Municipality", "Province","Birth Date","Age", "Gender",
                "Civil Status", "Diagnosis", "Type of Service", "Referral To",        
                "Seen by Doctor", "Disposition", "Time if Admit", "Doctor", 
                "Phone", "Email","Birth Place", "Nationality",
                "Medical History", "Registration Date", "Registered By",
            ]
            ws.append(headers)

            for patient in patients.values():
                ws.append([
                    patient.get("case_number", ""),
                    patient.get("patient_id", ""),
                    patient.get("arrival_time", ""),
                    patient.get("first_name", ""),
                    patient.get("middle_name", ""),
                    patient.get("last_name", ""),
                    patient.get("barangay", ""),
                    patient.get("municipality", ""),
                    patient.get("province", ""),
                    patient.get("birth_date", ""),
                    patient.get("age", ""),
                    patient.get("gender", ""),
                    patient.get("civil_status", ""),
                    patient.get("diagnosis", ""),
                    patient.get("service_type", ""),
                    patient.get("referred_to", ""),
                    patient.get("seen_by_doctor", ""),
                    patient.get("disposition", ""),
                    patient.get("time_if_admit", ""),
                    patient.get("doctor", ""),
                    patient.get("phone", ""),
                    patient.get("email", ""),
                    patient.get("birth_place", ""),
                    patient.get("nationality", ""),
                    patient.get("medical_history", ""),
                    patient.get("registration_date", ""),
                    patient.get("registered_by", ""),
                ])

            wb.save(file_path)
            messagebox.showinfo("Export Complete", f"ER patient report saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report:\n{e}")

    Label(content, text="Export all ER patient registration data to a Microsoft Excel worksheet.",
          font=FONT["body"], bg=T["bg"], fg=T["text"]).pack(anchor=W, pady=(0, 4))

    export_btn = Button(content, text="Export ER Report", command=export_to_excel,
                        bg=T["accent"], fg=T["white"], font=FONT["body_b"],
                        bd=0, relief=FLAT, padx=14, pady=10, cursor="hand2")
    export_btn.pack(anchor=W, pady=(12, 0))

    if page_refreshers is not None:
        def refresh_er_report_page():
            return build_er_report_page(parent, page_refreshers)
        page_refreshers["er_report"] = refresh_er_report_page

    return frame
