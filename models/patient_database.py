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

    def __init__(self):
        self.db = DatabaseConnection()
        if not self.db.connect():
            raise Exception("Failed to connect to database")
        self.db.create_tables()

    def generate_next_patient_id(self):
        """Generate the next available patient ID starting from 30000."""
        query = "SELECT MAX(CAST(patient_id AS UNSIGNED)) FROM patients WHERE CAST(patient_id AS UNSIGNED) >= %s"
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

    def _normalize_birth_date(self, date_text):
        """Convert MM-DD-YYYY input into YYYY-MM-DD for SQL storage."""
        if not date_text:
            return None
        try:
            return datetime.strptime(date_text, "%m-%d-%Y").strftime("%Y-%m-%d")
        except ValueError:
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
        return date_value.strftime("%m-%d-%Y")

    def add_patient(self, patient_id, data):
        """Add a new patient to the database."""
        insert_query = """
        INSERT INTO patients (patient_id, first_name, middle_name, last_name, age, gender,
            birth_date, birth_place, civil_status, nationality, registered_by,
            phone, email, barangay, municipality, province, medical_history, registration_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        birth_date_value = self._normalize_birth_date(data.get('birth_date'))
        try:
            self.db.execute_query(insert_query, (
                patient_id,
                data.get('first_name', ''),
                data.get('middle_name', ''),
                data.get('last_name', ''),
                data.get('age', ''),
                data.get('gender', ''),
                birth_date_value,
                data.get('birth_place', ''),
                data.get('civil_status', ''),
                data.get('nationality', ''),
                data.get('registered_by', ''),
                data.get('phone', ''),
                data.get('email', ''),
                data.get('barangay', ''),
                data.get('municipality', ''),
                data.get('province', ''),
                data.get('medical_history', '')
            ))
            self.db.commit()
            return True
        except Error as e:
            print(f"Error adding patient: {e}")
            return False

    def _map_patient_row(self, row):
        """Map a raw patient row tuple into a dictionary."""
        return {
            'id': row[0],
            'patient_id': row[1],
            'first_name': row[2],
            'middle_name': row[3],
            'last_name': row[4],
            'age': row[5],
            'gender': row[6],
            'birth_date': self._format_birth_date_for_output(row[7]),
            'birth_place': row[8],
            'civil_status': row[9],
            'nationality': row[10],
            'registered_by': row[11],
            'phone': row[12],
            'email': row[13],
            'barangay': row[14],
            'municipality': row[15],
            'province': row[16],
            'medical_history': row[17],
            'registration_date': str(row[18]) if row[18] else None
        }

    def get_patient(self, patient_id):
        """Get patient by ID."""
        query = (
            "SELECT id, patient_id, first_name, middle_name, last_name, age, gender, birth_date, "
            "birth_place, civil_status, nationality, registered_by, phone, email, barangay, "
            "municipality, province, medical_history, registration_date FROM patients WHERE patient_id = %s"
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
            "SELECT id, patient_id, first_name, middle_name, last_name, age, gender, birth_date, "
            "birth_place, civil_status, nationality, registered_by, phone, email, barangay, "
            "municipality, province, medical_history, registration_date FROM patients ORDER BY registration_date DESC"
        )
        cursor = self.db.execute_query(query)
        patients = {}
        if cursor:
            for row in cursor.fetchall():
                patients[row[1]] = self._map_patient_row(row)
        return patients

    def search_patients(self, search_term):
        """Search patients by ID or name."""
        like_term = f"%{search_term}%"
        query = (
            "SELECT id, patient_id, first_name, middle_name, last_name, age, gender, birth_date, "
            "birth_place, civil_status, nationality, registered_by, phone, email, barangay, "
            "municipality, province, medical_history, registration_date FROM patients "
            "WHERE UPPER(patient_id) LIKE %s OR UPPER(first_name) LIKE %s "
            "OR UPPER(middle_name) LIKE %s OR UPPER(last_name) LIKE %s "
            "OR UPPER(CONCAT(first_name, ' ', last_name)) LIKE %s "
            "OR UPPER(CONCAT(last_name, ' ', first_name)) LIKE %s "
            "ORDER BY registration_date DESC"
        )
        cursor = self.db.execute_query(
            query, (like_term, like_term, like_term, like_term, like_term, like_term))
        patients = {}
        if cursor:
            for row in cursor.fetchall():
                patients[row[1]] = self._map_patient_row(row)
        return patients

    def update_patient(self, patient_id, data):
        """Update patient record by ID."""
        query = (
            "UPDATE patients SET first_name = %s, middle_name = %s, last_name = %s, age = %s, "
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
                data.get('age', ''),
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

    def patient_exists(self, patient_id):
        """Check if patient exists."""
        query = "SELECT COUNT(*) FROM patients WHERE patient_id = %s"
        cursor = self.db.execute_query(query, (patient_id,))
        if cursor:
            return cursor.fetchone()[0] > 0
        return False

    def has_duplicate_patient(self, data):
        """Check if a patient with the same name and birth date already exists."""
        conditions = []
        params = []

        if data.get('first_name') and data.get('last_name') and data.get('birth_date'):
            normalized_birth_date = self._normalize_birth_date(data['birth_date'])
            conditions.append("(first_name = %s AND last_name = %s AND birth_date <=> %s)")
            params.extend([data['first_name'], data['last_name'], normalized_birth_date])

        if not conditions:
            return False

        query = f"SELECT COUNT(*) FROM patients WHERE {' OR '.join(conditions)}"
        cursor = self.db.execute_query(query, tuple(params))
        if cursor:
            return cursor.fetchone()[0] > 0
        return False
