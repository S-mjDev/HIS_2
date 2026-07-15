import os
import sys
from datetime import datetime
from mysql.connector import Error

try:
    from models.database import get_connection
except ModuleNotFoundError:
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if ROOT_DIR not in sys.path:
        sys.path.insert(0, ROOT_DIR)
    from models.database import get_connection


class VisitDatabase:
    """Handles visits and admissions tables."""

    VISIT_STARTING = 10000

    def __init__(self):
        self.db = get_connection()

    # ── Visit number generation ────────────────────────────
    def generate_next_visit_no(self, prefix="V"):
        query = """
        SELECT MAX(CAST(SUBSTRING(visit_no, %s) AS UNSIGNED))
        FROM visits
        WHERE visit_no LIKE %s
        """
        cursor = self.db.execute_query(query, (len(prefix) + 1, f"{prefix}%"))
        if cursor:
            result = cursor.fetchone()
            if result and result[0]:
                return f"{prefix}{int(result[0]) + 1:05d}"
        return f"{prefix}{self.VISIT_STARTING:05d}"

    def generate_next_case_number(self):
        query = """
        SELECT MAX(CAST(SUBSTRING(case_number, 4) AS UNSIGNED))
        FROM visits
        WHERE case_number IS NOT NULL AND case_number <> ''
        """
        cursor = self.db.execute_query(query)
        if cursor:
            result = cursor.fetchone()
            if result and result[0]:
                return f"ER-{int(result[0]) + 1:04d}"
        return "ER-0001"

    # ── Add visit ─────────────────────────────────────────
    def add_visit(self, data):
        """Insert a new visit row. Returns visit_no on success."""
        visit_type = data.get("visit_type", "OPD").upper()
        prefix_map = {"OPD": "V", "ER": "E", "IPD": "I"}
        prefix     = prefix_map.get(visit_type, "V")
        visit_no   = data.get("visit_no") or self.generate_next_visit_no(prefix)

        # Parse arrival_time string → TIME
        arrival_raw = data.get("arrival_time", "")
        arrival_time = None
        if arrival_raw:
            for fmt in ["%I:%M %p", "%H:%M"]:
                try:
                    arrival_time = datetime.strptime(
                        arrival_raw.strip().upper(), fmt).strftime("%H:%M:%S")
                    break
                except ValueError:
                    continue

        query = """
        INSERT INTO visits (
            visit_no, patient_id, visit_type, case_number,
            visit_date, arrival_time, diagnosis, service_type,
            referred_to, seen_by_doctor, disposition, doctor, registered_by
        ) VALUES (%s,%s,%s,%s, NOW(),%s,%s,%s, %s,%s,%s,%s,%s)
        """
        try:
            self.db.execute_query(query, (
                visit_no,
                data.get("patient_id", ""),
                visit_type,
                data.get("case_number") or None,
                arrival_time,
                data.get("diagnosis", ""),
                data.get("service_type", ""),
                data.get("referred_to", ""),
                data.get("seen_by_doctor", ""),
                data.get("disposition", ""),
                data.get("doctor", ""),
                data.get("registered_by", ""),
            ))
            self.db.commit()
            return visit_no
        except Error as e:
            print(f"Error adding visit: {e}")
            try:
                self.db.connection.rollback()
            except Exception:
                pass
            return None

    # ── Add admission ─────────────────────────────────────
    def add_admission(self, visit_id, data):
        """Insert an admission record linked to a visit."""
        query = """
        INSERT INTO admissions (
            visit_id, patient_id, admission_date,
            ward, room_no, bed_no, attending_doctor,
            status, remarks
        ) VALUES (%s,%s,NOW(), %s,%s,%s,%s, 'ADMITTED',%s)
        """
        try:
            self.db.execute_query(query, (
                visit_id,
                data.get("patient_id", ""),
                data.get("ward", ""),
                data.get("room_no", ""),
                data.get("bed_no", ""),
                data.get("attending_doctor", ""),
                data.get("remarks", ""),
            ))
            self.db.commit()
            return True
        except Error as e:
            print(f"Error adding admission: {e}")
            return False

    def get_visit_id(self, visit_no):
        """Get visit_id from visit_no."""
        cursor = self.db.execute_query(
            "SELECT visit_id FROM visits WHERE visit_no = %s", (visit_no,))
        if cursor:
            row = cursor.fetchone()
            return row[0] if row else None
        return None

    # ── Discharge ─────────────────────────────────────────
    def discharge_patient(self, admission_id, remarks="", time_of_discharged_dr_order=None):
        """Mark an admission as discharged."""
        query = """
        UPDATE admissions
        SET status = 'DISCHARGED', discharge_date = NOW(), remarks = %s, time_of_discharged_dr_order = %s
        WHERE admission_id = %s
        """
        try:
            self.db.execute_query(query, (remarks, time_of_discharged_dr_order, admission_id))
            self.db.commit()
            return True
        except Error as e:
            print(f"Error discharging patient: {e}")
            return False

    # ── Get admitted patients ─────────────────────────────
    def get_admitted_patients(self):
        """Get all currently admitted patients with patient + visit info."""
        query = """
        SELECT
            a.admission_id, a.patient_id, a.admission_date,
            a.ward, a.room_no, a.bed_no, a.attending_doctor,
            a.status, a.discharge_date, a.remarks,
            p.first_name, p.middle_name, p.last_name,
            p.gender, p.birth_date, p.phone,
            v.visit_no, v.visit_id, v.diagnosis
        FROM admissions a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN visits   v ON a.visit_id   = v.visit_id
        WHERE a.status = 'ADMITTED'
        ORDER BY a.admission_date DESC
        """
        cursor = self.db.execute_query(query)
        result = {}
        if cursor:
            for row in cursor.fetchall():
                result[row[0]] = {
                    "admission_id":     row[0],
                    "patient_id":       row[1],
                    "admission_date":   str(row[2]) if row[2] else "",
                    "ward":             row[3] or "",
                    "room_no":          row[4] or "",
                    "bed_no":           row[5] or "",
                    "attending_doctor": row[6] or "",
                    "status":           row[7] or "",
                    "discharge_date":   str(row[8]) if row[8] else "",
                    "remarks":          row[9] or "",
                    "first_name":       row[10] or "",
                    "middle_name":      row[11] or "",
                    "last_name":        row[12] or "",
                    "gender":           row[13] or "",
                    "birth_date":       str(row[14]) if row[14] else "",
                    "phone":            row[15] or "",
                    "visit_no":         row[16] or "",
                    "visit_id":         row[17],
                    "diagnosis":        row[18] or "",
                }
        return result

    def get_all_admissions(self):
        """Get all admissions including discharged."""
        query = """
        SELECT
            a.admission_id, a.patient_id, a.admission_date,
            a.ward, a.room_no, a.bed_no, a.attending_doctor,
            a.status, a.discharge_date, a.remarks,
            a.time_of_discharged_dr_order,
            p.first_name, p.middle_name, p.last_name,
            p.gender, v.visit_no, v.diagnosis
        FROM admissions a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN visits   v ON a.visit_id   = v.visit_id
        ORDER BY a.admission_date DESC
        """
        cursor = self.db.execute_query(query)
        result = {}
        if cursor:
            for row in cursor.fetchall():
                result[row[0]] = {
                    "admission_id":     row[0],
                    "patient_id":       row[1],
                    "admission_date":   str(row[2]) if row[2] else "",
                    "ward":             row[3] or "",
                    "room_no":          row[4] or "",
                    "bed_no":           row[5] or "",
                    "attending_doctor": row[6] or "",
                    "status":           row[7] or "",
                    "discharge_date":   str(row[8]) if row[8] else "",
                    "remarks":          row[9] or "",

                    # Correct position
                    "time_of_discharged_dr_order": str(row[10]) if row[10] else "",

                    # Patient information
                    "first_name":       row[11] or "",
                    "middle_name":      row[12] or "",
                    "last_name":        row[13] or "",
                    "gender":           row[14] or "",

                    # Visit information
                    "visit_no":         row[15] or "",
                    "diagnosis":        row[16] or "",
                }
        return result

    # ── Stats ─────────────────────────────────────────────
    def count_admitted_today(self):
        query = """
        SELECT COUNT(*) FROM admissions
        WHERE DATE(admission_date) = CURDATE() AND status = 'ADMITTED'
        """
        cursor = self.db.execute_query(query)
        return cursor.fetchone()[0] if cursor else 0

    def count_total_admitted(self):
        query = "SELECT COUNT(*) FROM admissions WHERE status = 'ADMITTED'"
        cursor = self.db.execute_query(query)
        return cursor.fetchone()[0] if cursor else 0
