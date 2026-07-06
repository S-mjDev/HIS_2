import os
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from models.patient_database import PatientDatabase
from utils.theme import T, FONT
from utils.widgets import mk_entry, page_header
from utils.validators import validate_date

try:
    import openpyxl
    from openpyxl.workbook import Workbook
    from openpyxl.styles import (
        PatternFill, Font, Alignment, Border, Side, GradientFill
    )
    from openpyxl.utils import get_column_letter
except ImportError:
    openpyxl = None


# ── Colour palette (matches app theme) ───────────────────
XL_ACCENT      = "2563EB"   # blue
XL_ACCENT_DARK = "1D4ED8"
XL_SIDEBAR     = "1A2332"   # dark navy
XL_HEADING_BG  = "F1F5F9"   # light grey
XL_ROW_EVEN    = "F8FAFC"
XL_ROW_ODD     = "FFFFFF"
XL_BORDER      = "E2E8F0"
XL_TEXT        = "1E293B"
XL_MUTED       = "64748B"
XL_WHITE       = "FFFFFF"
XL_SUCCESS     = "059669"
XL_WARNING     = "D97706"


def _border(color=XL_BORDER, style="thin"):
    s = Side(border_style=style, color=color)
    return Border(left=s, right=s, top=s, bottom=s)

def _fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def _font(bold=False, color=XL_TEXT, size=9, italic=False):
    return Font(name="Calibri", bold=bold, color=color,
                size=size, italic=italic)

def _align(h="left", v="center", wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)


def build_er_report_page(parent, page_refreshers=None):
    frame = Frame(parent, bg=T["bg"])
    page_header(frame, "ER Patient Report",
                "Export ER patient registration data to Excel")

    db_container = {"instance": PatientDatabase()}

    content = Frame(frame, bg=T["bg"])
    content.pack(fill=BOTH, expand=True, padx=24, pady=16)

    def _normalize_date(date_text):
        for fmt in ["%m-%d-%Y", "%m/%d/%Y", "%Y-%m-%d",
                    "%B %d, %Y", "%b %d, %Y"]:
            try:
                return datetime.strptime(date_text, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    def refresh_database():
        try:
            db_container["instance"] = PatientDatabase()
            return True
        except Exception as e:
            messagebox.showerror("Database Error",
                                 f"Failed to refresh database:\n{e}")
            return False

    # ── Filter card ───────────────────────────────────────
    filter_card = Frame(content, bg=T["panel"],
                        highlightthickness=1,
                        highlightbackground=T["border"])
    filter_card.pack(fill=X, pady=(0, 18))
    fb = Frame(filter_card, bg=T["panel"])
    fb.pack(fill=X, padx=20, pady=16)

    Label(fb, text="EXPORT FILTER", font=FONT["tag"],
          bg=T["panel"], fg=T["accent"]).grid(
        row=0, column=0, columnspan=4, sticky=W)
    Label(fb, text="Exports ER-registered patients only.",
          font=FONT["body"], bg=T["panel"],
          fg=T["muted"]).grid(row=1, column=0, columnspan=4,
                              sticky=W, pady=(4, 12))

    Label(fb, text="START DATE", font=FONT["tag"],
          bg=T["panel"], fg=T["muted"]).grid(
        row=2, column=0, sticky=W, pady=(0, 4))
    from_entry = mk_entry(fb, width=18)
    from_entry.grid(row=3, column=0, sticky=W)

    Label(fb, text="END DATE", font=FONT["tag"],
          bg=T["panel"], fg=T["muted"]).grid(
        row=2, column=1, sticky=W, pady=(0, 4), padx=(24, 0))
    to_entry = mk_entry(fb, width=18)
    to_entry.grid(row=3, column=1, sticky=W, padx=(24, 0))

    Label(fb, text="Format: MM-DD-YYYY or YYYY-MM-DD",
          font=FONT["small"], bg=T["panel"],
          fg=T["muted"]).grid(row=4, column=0, columnspan=3,
                              sticky=W, pady=(6, 0))

    if openpyxl is None:
        Label(content,
              text="⚠  openpyxl is required.  Run: pip install openpyxl",
              font=FONT["body"], bg=T["bg"],
              fg=T["danger"]).pack(anchor=W, pady=12)
        return frame

    # ── Excel export ──────────────────────────────────────
    def export_to_excel():
        if not refresh_database():
            return

        start_raw = from_entry.get().strip()
        end_raw   = to_entry.get().strip()
        start_date = end_date = None

        if start_raw:
            if not validate_date(start_raw):
                messagebox.showerror("Invalid Date",
                    "Start date must be MM-DD-YYYY or YYYY-MM-DD.")
                return
            start_date = _normalize_date(start_raw)
        if end_raw:
            if not validate_date(end_raw):
                messagebox.showerror("Invalid Date",
                    "End date must be MM-DD-YYYY or YYYY-MM-DD.")
                return
            end_date = _normalize_date(end_raw)
        if start_date and end_date and start_date > end_date:
            messagebox.showerror("Invalid Range",
                "Start date cannot be after end date.")
            return

        patients = db_container["instance"].get_patients(
            er_only=True,
            start_date=start_date,
            end_date=end_date
        )
        if not patients:
            messagebox.showinfo("No Data",
                "No ER patient records found for the selected range.")
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

            # ── Title block ───────────────────────────────
            date_label = ""
            if start_date and end_date:
                date_label = f"  {start_date}  to  {end_date}"
            elif start_date:
                date_label = f"  From  {start_date}"
            elif end_date:
                date_label = f"  Up to  {end_date}"

            ws.merge_cells("A1:Z1")
            t1 = ws["A1"]
            t1.value = "HOSPITAL INFORMATION SYSTEM"
            t1.font      = _font(bold=True, color=XL_WHITE, size=14)
            t1.fill      = _fill(XL_SIDEBAR)
            t1.alignment = _align("center")

            ws.merge_cells("A2:Z2")
            t2 = ws["A2"]
            t2.value = f"ER PATIENT REPORT{date_label}"
            t2.font      = _font(bold=True, color=XL_WHITE, size=11)
            t2.fill      = _fill(XL_ACCENT)
            t2.alignment = _align("center")

            ws.merge_cells("A3:Z3")
            t3 = ws["A3"]
            t3.value = (
                f"Generated: {datetime.now().strftime('%B %d, %Y  %I:%M %p')}  "
                f"  |  Total Records: {len(patients)}"
            )
            t3.font      = _font(italic=True, color=XL_MUTED, size=9)
            t3.fill      = _fill(XL_HEADING_BG)
            t3.alignment = _align("center")

            ws.row_dimensions[1].height = 26
            ws.row_dimensions[2].height = 22
            ws.row_dimensions[3].height = 16

            ws.append([])  # blank row 4

            # ── Column headers (row 5) ────────────────────
            headers = [
                ("Case No.",        10),
                ("Patient ID",      12),
                ("Arrival Time",    14),
                ("First Name",      16),
                ("Middle Name",     14),
                ("Last Name",       16),
                ("Age",              6),
                ("Gender",           9),
                ("Civil Status",    13),
                ("Birth Date",      14),
                ("Birth Place",     16),
                ("Nationality",     13),
                ("Barangay",        18),
                ("Municipality",    16),
                ("Province",        14),
                ("Phone",           14),
                ("Email",           22),
                ("Diagnosis",       22),
                ("Type of Service", 18),
                ("Referral To",     18),
                ("Seen by Doctor",  16),
                ("Disposition",     16),
                ("Time if Admit",   14),
                ("Doctor",          18),
                ("Medical History", 22),
                ("Registered By",   14),
                ("Registration Date", 20),
            ]

            header_row = 5
            for col_idx, (label, width) in enumerate(headers, start=1):
                cell = ws.cell(row=header_row, column=col_idx, value=label)
                cell.font      = _font(bold=True, color=XL_WHITE, size=9)
                cell.fill      = _fill(XL_ACCENT)
                cell.alignment = _align("center")
                cell.border    = _border(XL_ACCENT_DARK)
                col_letter = get_column_letter(col_idx)
                ws.column_dimensions[col_letter].width = width

            ws.row_dimensions[header_row].height = 20

            # ── Data rows ─────────────────────────────────
            for row_idx, patient in enumerate(patients.values(), start=header_row + 1):
                is_even = (row_idx - header_row) % 2 == 0
                row_fill = _fill(XL_ROW_EVEN if is_even else XL_ROW_ODD)

                row_data = [
                    patient.get("case_number",      ""),
                    patient.get("patient_id",       ""),
                    patient.get("arrival_time",     ""),
                    patient.get("first_name",       ""),
                    patient.get("middle_name",      ""),
                    patient.get("last_name",        ""),
                    patient.get("age",              ""),
                    patient.get("gender",           ""),
                    patient.get("civil_status",     ""),
                    patient.get("birth_date",       ""),
                    patient.get("birth_place",      ""),
                    patient.get("nationality",      ""),
                    patient.get("barangay",         ""),
                    patient.get("municipality",     ""),
                    patient.get("province",         ""),
                    patient.get("phone",            ""),
                    patient.get("email",            ""),
                    patient.get("diagnosis",        ""),
                    patient.get("service_type",     ""),
                    patient.get("referred_to",      ""),
                    patient.get("seen_by_doctor",   ""),
                    patient.get("disposition",      ""),
                    patient.get("time_if_admit",    ""),
                    patient.get("doctor",           ""),
                    patient.get("medical_history",  ""),
                    patient.get("registered_by",    ""),
                    patient.get("registration_date",""),
                ]

                for col_idx, value in enumerate(row_data, start=1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=value)
                    cell.fill      = row_fill
                    cell.border    = _border()
                    cell.alignment = _align("center" if col_idx <= 3 else "left",
                                            wrap=col_idx in (18, 25))
                    cell.font      = _font(size=9)

                    # Highlight Case Number column
                    if col_idx == 1 and value:
                        cell.font = _font(bold=True, color=XL_ACCENT, size=9)

                ws.row_dimensions[row_idx].height = 16

            # ── Freeze panes & auto-filter ─────────────────
            ws.freeze_panes = "A6"
            ws.auto_filter.ref = (
                f"A{header_row}:{get_column_letter(len(headers))}{header_row}"
            )

            # ── Summary footer ─────────────────────────────
            footer_row = header_row + len(patients) + 2
            ws.merge_cells(
                f"A{footer_row}:{get_column_letter(len(headers))}{footer_row}"
            )
            footer = ws[f"A{footer_row}"]
            footer.value = (
                f"END OF REPORT  |  Total: {len(patients)} record(s)  |  "
                f"Exported: {datetime.now().strftime('%B %d, %Y')}"
            )
            footer.font      = _font(italic=True, color=XL_MUTED, size=8)
            footer.fill      = _fill(XL_HEADING_BG)
            footer.alignment = _align("center")
            footer.border    = _border()

            # ── Print settings ─────────────────────────────
            ws.page_setup.orientation = "landscape"
            ws.page_setup.fitToPage   = True
            ws.page_setup.fitToWidth  = 1
            ws.page_setup.fitToHeight = 0

            wb.save(file_path)
            messagebox.showinfo("Export Complete",
                f"ER report saved to:\n{file_path}\n\n"
                f"{len(patients)} record(s) exported.")

        except Exception as e:
            messagebox.showerror("Export Error",
                                 f"Failed to export report:\n{e}")

    # ── Buttons ───────────────────────────────────────────
    Label(content,
          text="Export all ER patient registration data to a styled Excel worksheet.",
          font=FONT["body"], bg=T["bg"], fg=T["text"]).pack(anchor=W, pady=(0, 4))

    status_lbl = Label(content, text="",
                       font=FONT["small"], bg=T["bg"], fg=T["muted"])
    status_lbl.pack(anchor=W, pady=(0, 12))

    def refresh_with_status():
        if refresh_database():
            status_lbl.config(
                text=f"✓ Data refreshed at {datetime.now().strftime('%H:%M:%S')}",
                fg=T["success"])
            status_lbl.after(3000, lambda: status_lbl.config(
                text="Database ready.", fg=T["muted"]))

    bf = Frame(content, bg=T["bg"])
    bf.pack(anchor=W)
    Button(bf, text="Export ER Report", command=export_to_excel,
           bg=T["accent"], fg=T["white"], font=FONT["body_b"],
           bd=0, relief=FLAT, padx=14, pady=10,
           cursor="hand2").pack(side=LEFT, padx=(0, 10))
    Button(bf, text="Refresh Data", command=refresh_with_status,
           bg=T["border2"], fg=T["text"], font=FONT["body_b"],
           bd=0, relief=FLAT, padx=14, pady=10,
           cursor="hand2").pack(side=LEFT)

    refresh_with_status()

    if page_refreshers is not None:
        page_refreshers["er_report"] = lambda: build_er_report_page(
            parent, page_refreshers)

    return frame
