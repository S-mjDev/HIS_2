import os
import sys
from datetime import datetime
from mysql.connector import Error

try:
    from models.database import DatabaseConnection
except ModuleNotFoundError:
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if ROOT_DIR not in sys.path:
        sys.path.insert(0, ROOT_DIR)
    from models.database import DatabaseConnection


class PatientDatabase:
    """Handles all patient record operations: add, get, search, update, delete."""

    STARTING_ID = 30000
    starting_case_number = 10000

    def __init__(self):
        self.db = DatabaseConnection()
        if not self.db.connect():
            raise Exception("Failed to connect to database")
        self.db.create_tables()

    def generate_next_patient_id(self):
        """Generate the next available patient ID starting from 30000."""
        query = (
            "SELECT MAX(CAST(patient_id AS UNSIGNED)) "
            "FROM patients "
            "WHERE patient_id REGEXP '^[0-9]+$' "
            "AND CAST(patient_id AS UNSIGNED) >= %s"
        )
        cursor = self.db.execute_query(query, (self.STARTING_ID,))

        if cursor:
            result = cursor.fetchone()
            if result and result[0]:
                next_id = int(result[0]) + 1
            else:
                next_id = self.STARTING_ID
        else:
            next_id = self.STARTING_ID

        return str(next_id)
    
    def generate_next_case_number(self):
        """Generate the next ER case number (e.g. ER-00001)."""
        query = """
        SELECT MAX(CAST(SUBSTRING(case_number, 4) AS UNSIGNED))
        FROM (
            SELECT case_number FROM patients
            UNION ALL
            SELECT case_number FROM er_visits
        ) AS all_cases
        WHERE case_number REGEXP '^ER-[0-9]+$'
        """
        cursor = self.db.execute_query(query)
        if cursor:
            result = cursor.fetchone()
            if result and result[0]:
                next_num = int(result[0]) + 1
            else:
                next_num = self.starting_case_number
        else:
            next_num = self.starting_case_number
        return f"ER-{next_num:05d}"  # e.g. ER-00001, ER-00002

    def _next_case_number(self):
        query = """
        SELECT MAX(CAST(SUBSTRING(case_number, 4) AS UNSIGNED))
        FROM (
            SELECT case_number FROM patients
            UNION ALL
            SELECT case_number FROM er_visits
        ) AS all_cases
        WHERE case_number REGEXP '^ER-[0-9]+$'
        """
        cursor = self.db.execute_query(query)
        if cursor:
            result = cursor.fetchone()
            if result and result[0]:
                return f"ER-{int(result[0]) + 1:05d}"
        return f"ER-{self.starting_case_number:05d}"

    def _normalize_birth_date(self, date_text):
        """Convert MM-DD-YYYY input into YYYY-MM-DD for SQL storage."""
        if not date_text:
            return None
        formats = [
            "%m-%d-%Y",
            "%m/%d/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
            "%Y-%m-%d",  # Allow already normalized format
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_text, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    def _format_birth_date_for_output(self, date_value):
        """Convert stored SQL date into MM-DD-YYYY for display."""
        if not date_value:
            return None
        if isinstance(date_value, str):
            try:
                date_value = datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                return str(date_value)
        return date_value.strftime("%B %d, %Y")

    def _next_patient_id(self, patient_id=None):
        query = (
            "SELECT MAX(CAST(patient_id AS UNSIGNED)) "
            "FROM patients "
            "WHERE patient_id REGEXP '^[0-9]+$' "
            "AND CAST(patient_id AS UNSIGNED) >= %s FOR UPDATE"
        )
        cursor = self.db.execute_query(query, (self.STARTING_ID,))
        if cursor:
            result = cursor.fetchone()
            if result and result[0]:
                return str(int(result[0]) + 1)
        return str(self.STARTING_ID)

    def add_patient(self, patient_id_or_data, data=None, include_case_number=False):
        """Add a new patient to the database and return the assigned patient ID.
        Accepts add_patient(patient_id, data) or add_patient(data) where data contains "patient_id".
        Set include_case_number=True only for ER patient inserts when the patient row should also receive a case number.
        """
        if data is None:
            data = patient_id_or_data
            patient_id = data.get("patient_id", "")
        else:
            patient_id = patient_id_or_data
        insert_query = """
        INSERT INTO patients (patient_id, case_number, first_name, middle_name, last_name, gender,
            birth_date, birth_place, civil_status, nationality, age,
            arrival_time, diagnosis, service_type, referred_to, seen_by_doctor,
            disposition, time_if_admit, doctor, registered_by, phone, email,
            barangay, municipality, province, medical_history, registration_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW())
        """
        birth_date_value = self._normalize_birth_date(data.get('birth_date'))
        explicit_id = bool(patient_id)
        retries = 3

        while retries > 0:
            try:
                self.db.execute_query("START TRANSACTION")
                patient_id = self._next_patient_id(patient_id_or_data) if not patient_id else patient_id
                case_number = None
                if include_case_number:
                    case_number = data.get('case_number') or self._next_case_number()
                self.db.execute_query(insert_query, (
                    patient_id,
                    case_number,
                    data.get('first_name', ''),
                    data.get('middle_name', ''),
                    data.get('last_name', ''),
                    data.get('gender', ''),
                    birth_date_value,
                    data.get('birth_place', ''),
                    data.get('civil_status', ''),
                    data.get('nationality', ''),
                    data.get('age', ''),
                    data.get('arrival_time', ''),
                    data.get('diagnosis', ''),
                    data.get('service_type', ''),
                    data.get('referred_to', ''),
                    data.get('seen_by_doctor', ''),
                    data.get('disposition', ''),
                    data.get('time_if_admit', ''),
                    data.get('doctor', ''),
                    data.get('registered_by', ''),
                    data.get('phone', ''),
                    data.get('email', ''),
                    data.get('barangay', ''),
                    data.get('municipality', ''),
                    data.get('province', ''),
                    data.get('medical_history', '')
                ))
                self.db.commit()
                return patient_id
            except Error as e:
                if self.db.connection:
                    try:
                        self.db.connection.rollback()
                    except Exception:
                        pass
                if getattr(e, 'errno', None) == 1062 and 'patient_id' in str(e).lower():
                    if explicit_id:
                        print(f"Duplicate explicit patient_id detected on insert: {patient_id}")
                        return None
                    retries -= 1
                    if retries == 0:
                        print(f"Duplicate patient_id detected repeatedly on insert: {patient_id}")
                        return None
                    patient_id = ""
                    continue
                print(f"Error adding patient: {e}")
                return None

    def _map_patient_row(self, row):
        """Map a raw patient row tuple into a dictionary."""
        return {
            'id': row[0],
            'patient_id': row[1],
            'case_number': row[2],
            'first_name': row[3],
            'middle_name': row[4],
            'last_name': row[5],
            'gender': row[6],
            'birth_date': self._format_birth_date_for_output(row[7]),
            'birth_place': row[8],
            'civil_status': row[9],
            'nationality': row[10],
            'age': row[11],
            'arrival_time': row[12],
            'diagnosis': row[13],
            'service_type': row[14],
            'referred_to': row[15],
            'seen_by_doctor': row[16],
            'disposition': row[17],
            'time_if_admit': row[18],
            'doctor': row[19],
            'registered_by': row[20],
            'phone': row[21],
            'email': row[22],
            'barangay': row[23],
            'municipality': row[24],
            'province': row[25],
            'medical_history': row[26],
            'registration_date': str(row[27]) if row[27] else None
        }

    def get_patient(self, patient_id):
        """Get patient by ID."""
        query = (
            "SELECT id, patient_id, case_number, first_name, middle_name, last_name, gender, birth_date, "
            "birth_place, civil_status, nationality, age, arrival_time, diagnosis, service_type, "
            "referred_to, seen_by_doctor, disposition, time_if_admit, doctor, registered_by, phone, email, "
            "barangay, municipality, province, medical_history, registration_date "
            "FROM patients WHERE patient_id = %s"
        )
        cursor = self.db.execute_query(query, (patient_id,))
        if cursor:
            result = cursor.fetchone()
            if result:
                return self._map_patient_row(result)
        return None

    def get_all_patients(self):
        """Get all patients ordered by registration date."""
        query = (
            "SELECT id, patient_id, case_number, first_name, middle_name, last_name, gender, birth_date, "
            "birth_place, civil_status, nationality, age, arrival_time, diagnosis, service_type, "
            "referred_to, seen_by_doctor, disposition, time_if_admit, doctor, registered_by, phone, email, "
            "barangay, municipality, province, medical_history, registration_date "
            "FROM patients ORDER BY registration_date DESC"
        )
        cursor = self.db.execute_query(query)
        patients = {}
        if cursor:
            for row in cursor.fetchall():
                patients[row[1]] = self._map_patient_row(row)
        return patients

    def get_patients(self, er_only=False, start_date=None, end_date=None):
        """Get patients optionally filtered by ER fields and registration date range."""
        columns = (
            "id, patient_id, case_number, first_name, middle_name, last_name, gender, birth_date, "
            "birth_place, civil_status, nationality, age, arrival_time, diagnosis, service_type, "
            "referred_to, seen_by_doctor, disposition, time_if_admit, doctor, registered_by, phone, email, "
            "barangay, municipality, province, medical_history, registration_date"
        )
        conditions = []
        params = []

        if er_only:
            conditions.insert(0, "case_number IS NOT NULL AND case_number <> ''")

        if start_date and end_date:
            conditions.append("DATE(registration_date) BETWEEN %s AND %s")
            params.extend([start_date, end_date])
        elif start_date:
            conditions.append("DATE(registration_date) >= %s")
            params.append(start_date)
        elif end_date:
            conditions.append("DATE(registration_date) <= %s")
            params.append(end_date)

        if er_only:
            patient_query = f"SELECT {columns} FROM patients"
            er_query = f"SELECT {columns} FROM er_visits"
            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"
                patient_query += where_clause
                er_query += where_clause
            query = f"{patient_query} UNION ALL {er_query} ORDER BY registration_date DESC"
            query_params = tuple(params + params) if params else None
        else:
            base_query = f"SELECT {columns} FROM patients"
            if conditions:
                query = f"{base_query} WHERE {' AND '.join(conditions)} ORDER BY registration_date DESC"
            else:
                query = f"{base_query} ORDER BY registration_date DESC"
            query_params = tuple(params) if params else None

        cursor = self.db.execute_query(query, query_params)
        patients = {}
        if cursor:
            for row in cursor.fetchall():
                if er_only:
                    key = row[2] if row[2] else f"ER-{row[0]}"
                else:
                    key = row[1]
                patients[key] = self._map_patient_row(row)
        return patients

    def add_er_visit(self, patient_id, data):
        """Insert a new ER visit record without modifying the existing patient."""
        insert_query = """
        INSERT INTO er_visits (case_number, patient_id, first_name, middle_name, last_name, gender,
            birth_date, birth_place, civil_status, nationality, age,
            arrival_time, diagnosis, service_type, referred_to, seen_by_doctor,
            disposition, time_if_admit, doctor, registered_by, phone, email,
            barangay, municipality, province, medical_history, registration_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW())
        """
        birth_date_value = self._normalize_birth_date(data.get('birth_date'))
        case_number = data.get('case_number') or self._next_case_number()
        try:
            self.db.execute_query(insert_query, (
                case_number,
                patient_id,
                data.get('first_name', ''),
                data.get('middle_name', ''),
                data.get('last_name', ''),
                data.get('gender', ''),
                birth_date_value,
                data.get('birth_place', ''),
                data.get('civil_status', ''),
                data.get('nationality', ''),
                data.get('age', ''),
                data.get('arrival_time', ''),
                data.get('diagnosis', ''),
                data.get('service_type', ''),
                data.get('referred_to', ''),
                data.get('seen_by_doctor', ''),
                data.get('disposition', ''),
                data.get('time_if_admit', ''),
                data.get('doctor', ''),
                data.get('registered_by', ''),
                data.get('phone', ''),
                data.get('email', ''),
                data.get('barangay', ''),
                data.get('municipality', ''),
                data.get('province', ''),
                data.get('medical_history', '')
            ))
            self.db.commit()
            return case_number
        except Error as e:
            print(f"Error adding ER visit: {e}")
            return None

    def get_er_visit(self, case_number):
        """Get an ER visit by case number."""
        query = (
            "SELECT id, patient_id, case_number, first_name, middle_name, last_name, gender, birth_date, "
            "birth_place, civil_status, nationality, age, arrival_time, diagnosis, service_type, "
            "referred_to, seen_by_doctor, disposition, time_if_admit, doctor, registered_by, phone, email, "
            "barangay, municipality, province, medical_history, registration_date "
            "FROM er_visits WHERE case_number = %s"
        )
        cursor = self.db.execute_query(query, (case_number,))
        if cursor:
            result = cursor.fetchone()
            if result:
                return self._map_patient_row(result)
        return None

    def search_patients(self, search_term=None, first_name=None, last_name=None, case_number=None, er_only=False):
        """Search patients and ER visits by ID, name, or ER case number."""
        search_term = search_term.strip() if search_term else None
        first_name = first_name.strip() if first_name else None
        last_name = last_name.strip() if last_name else None
        case_number = case_number.strip() if case_number else None

        if not any([search_term, first_name, last_name, case_number]):
            return {}

        clauses = []
        params = []

        if case_number:
            clauses.append("UPPER(case_number) LIKE %s")
            params.append(f"%{case_number.upper()}%")

        if search_term:
            like_term = f"%{search_term.upper()}%"
            clauses.append(
                "(UPPER(patient_id) LIKE %s OR UPPER(case_number) LIKE %s OR "
                "UPPER(first_name) LIKE %s OR UPPER(middle_name) LIKE %s OR "
                "UPPER(last_name) LIKE %s OR UPPER(CONCAT(first_name, ' ', last_name)) LIKE %s OR "
                "UPPER(CONCAT(last_name, ' ', first_name)) LIKE %s)"
            )
            params.extend([like_term] * 7)

        if first_name and last_name:
            clauses.append("(UPPER(first_name) LIKE %s AND UPPER(last_name) LIKE %s)")
            params.append(f"%{first_name.upper()}%")
            params.append(f"%{last_name.upper()}%")
        elif first_name:
            clauses.append("UPPER(first_name) LIKE %s")
            params.append(f"%{first_name.upper()}%")
        elif last_name:
            clauses.append("UPPER(last_name) LIKE %s")
            params.append(f"%{last_name.upper()}%")

        where_clause = "WHERE " + " OR ".join(clauses)
        columns = (
            "id, patient_id, case_number, first_name, middle_name, last_name, gender, birth_date, "
            "birth_place, civil_status, nationality, age, arrival_time, diagnosis, service_type, "
            "referred_to, seen_by_doctor, disposition, time_if_admit, doctor, registered_by, phone, email, "
            "barangay, municipality, province, medical_history, registration_date"
        )

        if er_only:
            query = f"SELECT {columns}, 'er_visit' AS record_type FROM er_visits {where_clause} ORDER BY registration_date DESC"
            query_params = tuple(params)
        else:
            patient_query = f"SELECT {columns}, 'patient' AS record_type FROM patients {where_clause}"
            er_query = f"SELECT {columns}, 'er_visit' AS record_type FROM er_visits {where_clause}"
            query = f"{patient_query} UNION ALL {er_query} ORDER BY registration_date DESC"
            query_params = tuple(params + params)

        cursor = self.db.execute_query(query, query_params)
        patients = {}
        if cursor:
            for row in cursor.fetchall():
                record_type = row[-1]
                base_row = row[:-1]
                data = self._map_patient_row(base_row)
                data["record_type"] = record_type
                key = data["case_number"] if record_type == "er_visit" else data["patient_id"]
                patients[key] = data
        return patients

    def update_patient(self, patient_id, data):
        """Update patient record by ID."""
        query = (
            "UPDATE patients SET first_name = %s, middle_name = %s, last_name = %s, "
            "gender = %s, birth_date = %s, birth_place = %s, civil_status = %s, nationality = %s, "
            "age = %s, arrival_time = %s, diagnosis = %s, service_type = %s, referred_to = %s, "
            "seen_by_doctor = %s, disposition = %s, time_if_admit = %s, doctor = %s, "
            "phone = %s, email = %s, barangay = %s, municipality = %s, province = %s, "
            "medical_history = %s WHERE patient_id = %s"
        )
        birth_date_value = self._normalize_birth_date(data.get('birth_date'))
        try:
            self.db.execute_query(query, (
                data.get('first_name', ''),
                data.get('middle_name', ''),
                data.get('last_name', ''),
                data.get('gender', ''),
                birth_date_value,
                data.get('birth_place', ''),
                data.get('civil_status', ''),
                data.get('nationality', ''),
                data.get('age', ''),
                data.get('arrival_time', ''),
                data.get('diagnosis', ''),
                data.get('service_type', ''),
                data.get('referred_to', ''),
                data.get('seen_by_doctor', ''),
                data.get('disposition', ''),
                data.get('time_if_admit', ''),
                data.get('doctor', ''),
                data.get('phone', ''),
                data.get('email', ''),
                data.get('barangay', ''),
                data.get('municipality', ''),
                data.get('province', ''),
                data.get('medical_history', ''),
                patient_id
            ))
            self.db.commit()
            return True
        except Error as e:
            print(f"Error updating patient: {e}")
            return False

    def update_er_visit(self, case_number, data):
        """Update an ER visit record by case number."""
        query = (
            "UPDATE er_visits SET patient_id = %s, first_name = %s, middle_name = %s, last_name = %s, "
            "gender = %s, birth_date = %s, birth_place = %s, civil_status = %s, nationality = %s, "
            "age = %s, arrival_time = %s, diagnosis = %s, service_type = %s, referred_to = %s, "
            "seen_by_doctor = %s, disposition = %s, time_if_admit = %s, doctor = %s, registered_by = %s, "
            "phone = %s, email = %s, barangay = %s, municipality = %s, province = %s, "
            "medical_history = %s WHERE case_number = %s"
        )
        birth_date_value = self._normalize_birth_date(data.get('birth_date'))
        try:
            self.db.execute_query(query, (
                data.get('patient_id', ''),
                data.get('first_name', ''),
                data.get('middle_name', ''),
                data.get('last_name', ''),
                data.get('gender', ''),
                birth_date_value,
                data.get('birth_place', ''),
                data.get('civil_status', ''),
                data.get('nationality', ''),
                data.get('age', ''),
                data.get('arrival_time', ''),
                data.get('diagnosis', ''),
                data.get('service_type', ''),
                data.get('referred_to', ''),
                data.get('seen_by_doctor', ''),
                data.get('disposition', ''),
                data.get('time_if_admit', ''),
                data.get('doctor', ''),
                data.get('registered_by', ''),
                data.get('phone', ''),
                data.get('email', ''),
                data.get('barangay', ''),
                data.get('municipality', ''),
                data.get('province', ''),
                data.get('medical_history', ''),
                case_number
            ))
            self.db.commit()
            return True
        except Error as e:
            print(f"Error updating ER visit: {e}")
            return False

    def delete_patient(self, patient_id, data):
        """Update patient record by ID."""
        query = (
            "UPDATE patients SET first_name = %s, middle_name = %s, last_name = %s, "
            "gender = %s, birth_date = %s, birth_place = %s, civil_status = %s, nationality = %s, "
            "phone = %s, email = %s, barangay = %s, municipality = %s, province = %s, "
            "medical_history = %s WHERE patient_id = %s"
        )
        birth_date_value = self._normalize_birth_date(data.get('birth_date'))
        try:
            self.db.execute_query(query, (
                data.get('first_name', ''),
                data.get('middle_name', ''),
                data.get('last_name', ''),
                data.get('gender', ''),
                birth_date_value,
                data.get('birth_place', ''),
                data.get('civil_status', ''),
                data.get('nationality', ''),
                data.get('phone', ''),
                data.get('email', ''),
                data.get('barangay', ''),
                data.get('municipality', ''),
                data.get('province', ''),
                data.get('medical_history', ''),
                patient_id
            ))
            self.db.commit()
            return True
        except Error as e:
            print(f"Error updating patient: {e}")
            return False

    def delete_patient(self, patient_id):
        """Delete a patient record by ID."""
        try:
            self.db.execute_query("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
            self.db.commit()
            return True
        except Error as e:
            print(f"Error deleting patient: {e}")
            return False

    def delete_er_visit(self, case_number):
        """Delete an ER visit record by case number."""
        try:
            self.db.execute_query("DELETE FROM er_visits WHERE case_number = %s", (case_number,))
            self.db.commit()
            return True
        except Error as e:
            print(f"Error deleting ER visit: {e}")
            return False

    def patient_exists(self, patient_id):
        """Check if patient exists."""
        query = "SELECT COUNT(*) FROM patients WHERE patient_id = %s"
        cursor = self.db.execute_query(query, (patient_id,))
        if cursor:
            return cursor.fetchone()[0] > 0
        return False

    def has_duplicate_patient(self, data):
        """Return an existing patient_id for the same name and birth date, or None."""
        conditions = []
        params = []

        if data.get('first_name') and data.get('last_name') and data.get('birth_date'):
            normalized_birth_date = self._normalize_birth_date(data['birth_date'])
            conditions.append("(first_name = %s AND last_name = %s AND birth_date <=> %s)")
            params.extend([data['first_name'], data['last_name'], normalized_birth_date])

        if not conditions:
            return None

        query = f"SELECT patient_id FROM patients WHERE {' OR '.join(conditions)} LIMIT 1"
        cursor = self.db.execute_query(query, tuple(params))
        if cursor:
            result = cursor.fetchone()
            if result and result[0]:
                return result[0]
        return None

    def refresh_database_counter(self):
        """Refresh and synchronize the patient ID counter with the database.
        Call this after patient registration to avoid ID duplication in concurrent scenarios."""
        try:
            # Commit any pending transactions to ensure latest data
            self.db.commit()
            # Get the current maximum patient ID
            query = (
                "SELECT MAX(CAST(patient_id AS UNSIGNED)) "
                "FROM patients "
                "WHERE patient_id REGEXP '^[0-9]+$' "
                "AND CAST(patient_id AS UNSIGNED) >= %s"
            )
            cursor = self.db.execute_query(query, (self.STARTING_ID,))
            if cursor:
                result = cursor.fetchone()
                if result and result[0]:
                    return int(result[0]) + 1
            return self.STARTING_ID
        except Error as e:
            print(f"Error refreshing database counter: {e}")
            return None
