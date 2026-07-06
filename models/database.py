import os
import mysql.connector
from mysql.connector import Error

# FORCE PYINSTALLER TO TRACK THE AUTHENTICATION PLUGINS
from mysql.connector.plugins import mysql_native_password
from mysql.connector.plugins import caching_sha2_password

# Global connection singleton
_connection_instance = None
_initialized = False


def get_connection():
    """Get or create a persistent database connection (singleton pattern)."""
    global _connection_instance, _initialized
    if _connection_instance is None:
        _connection_instance = DatabaseConnection()
        if not _connection_instance.connect():
            raise Exception("Failed to connect to database")
    if not _initialized:
        _connection_instance.create_tables()
        _connection_instance.create_default_admin()
        _initialized = True
    return _connection_instance


class DatabaseConnection:
    """Manages the MySQL database connection and core query execution."""

    def __init__(self):
        self.host = os.getenv("DB_HOST", "192.168.1.88")
        self.database = os.getenv("DB_NAME", "his_db")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "root")
        self.connection = None

    def connect(self):
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                auth_plugin='mysql_native_password',
                use_pure=True,
                connection_timeout=300,
                autocommit=False
            )
            
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False

    def disconnect(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query, params=None):
        """Execute a query and return cursor."""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Error as e:
            print(f"Error executing query: {e}")
            return None

    def commit(self):
        """Commit changes."""
        if self.connection:
            self.connection.commit()

    def create_tables(self):
        """Create necessary database tables."""
        users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'Staff',
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME NULL
        )
        """

        patients_table = """
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            case_number VARCHAR(20) UNIQUE NULL,
            patient_id VARCHAR(20) UNIQUE NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            middle_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            gender VARCHAR(10),
            birth_date DATE,
            birth_place VARCHAR(100),
            civil_status VARCHAR(20),
            nationality VARCHAR(50),
            age VARCHAR(10),
            arrival_time VARCHAR(50),
            diagnosis TEXT,
            service_type VARCHAR(100),
            referred_to VARCHAR(100),
            seen_by_doctor VARCHAR(100),
            disposition VARCHAR(50),
            time_if_admit VARCHAR(50),
            doctor VARCHAR(100),
            registered_by VARCHAR(50),
            phone VARCHAR(15),
            email VARCHAR(100),
            barangay TEXT,
            medical_history TEXT,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """

        er_visits_table = """
        CREATE TABLE IF NOT EXISTS er_visits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            case_number VARCHAR(20) UNIQUE NOT NULL,
            patient_id VARCHAR(20) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            middle_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            gender VARCHAR(10),
            birth_date DATE,
            birth_place VARCHAR(100),
            civil_status VARCHAR(20),
            nationality VARCHAR(50),
            age VARCHAR(10),
            arrival_time VARCHAR(50),
            diagnosis TEXT,
            service_type VARCHAR(100),
            referred_to VARCHAR(100),
            seen_by_doctor VARCHAR(100),
            disposition VARCHAR(50),
            time_if_admit VARCHAR(50),
            doctor VARCHAR(100),
            registered_by VARCHAR(50),
            phone VARCHAR(15),
            email VARCHAR(100),
            barangay TEXT,
            municipality VARCHAR(100),
            province VARCHAR(100),
            medical_history TEXT,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """

        try:
            self.execute_query(users_table)
            self.execute_query(patients_table)
            self.execute_query(er_visits_table)
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'nationality'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN nationality VARCHAR(50)")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'registered_by'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN registered_by VARCHAR(50)")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'municipality'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN municipality VARCHAR(100)")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'province'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN province VARCHAR(100)")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'case_number'")
            if cursor:
                row = cursor.fetchone()
                if not row:
                    self.execute_query("ALTER TABLE patients ADD COLUMN case_number VARCHAR(20) UNIQUE NULL")
                else:
                    try:
                        if row[2] == 'NO':
                            self.execute_query("ALTER TABLE patients MODIFY COLUMN case_number VARCHAR(20) UNIQUE NULL")
                    except Exception:
                        pass
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'age'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN age VARCHAR(10)")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'arrival_time'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN arrival_time VARCHAR(50)")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'diagnosis'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN diagnosis TEXT")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'service_type'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN service_type VARCHAR(100)")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'referred_to'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN referred_to VARCHAR(100)")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'seen_by_doctor'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN seen_by_doctor VARCHAR(100)")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'time_if_admit'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN time_if_admit VARCHAR(50)")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'doctor'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN doctor VARCHAR(100)")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'disposition'")
            if cursor and not cursor.fetchone():
                self.execute_query("ALTER TABLE patients ADD COLUMN disposition VARCHAR(50)")
            cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'address'")
            if cursor and cursor.fetchone():
                # Migrate address to barangay if it exists
                self.execute_query("ALTER TABLE patients ADD COLUMN barangay TEXT")
                self.execute_query("UPDATE patients SET barangay = address WHERE barangay IS NULL")
                self.execute_query("ALTER TABLE patients DROP COLUMN address")
            else:
                cursor = self.execute_query("SHOW COLUMNS FROM patients LIKE 'barangay'")
                if cursor and not cursor.fetchone():
                    self.execute_query("ALTER TABLE patients ADD COLUMN barangay TEXT")
            self.commit()
            print("Database tables created successfully")
        except Error as e:
            print(f"Error creating tables: {e}")

    def create_default_admin(self):
        """Create default admin user if not exists."""
        import hashlib
        try:
            check_query = "SELECT COUNT(*) FROM users WHERE username = 'admin'"
            cursor = self.execute_query(check_query)
            if cursor and cursor.fetchone()[0] == 0:
                insert_query = """
                INSERT INTO users (username, password, role, created_date)
                VALUES (%s, %s, %s, NOW())
                """
                hashed_pw = hashlib.sha256('admin123'.encode()).hexdigest()
                self.execute_query(insert_query, ('admin', hashed_pw, 'Administrator'))
                self.commit()
                print("Default admin user created")
        except Error as e:
            print(f"Error creating default admin: {e}")
