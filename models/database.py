import os
import mysql.connector
from mysql.connector import Error

# FORCE PYINSTALLER TO TRACK THE AUTHENTICATION PLUGINS
from mysql.connector.plugins import mysql_native_password
from mysql.connector.plugins import caching_sha2_password


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
                use_pure=True
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
            patient_id VARCHAR(20) UNIQUE NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            middle_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            age INT,
            gender VARCHAR(10),
            birth_date DATE,
            birth_place VARCHAR(100),
            civil_status VARCHAR(20),
            nationality VARCHAR(50),
            registered_by VARCHAR(50),
            phone VARCHAR(15),
            email VARCHAR(100),
            barangay TEXT,
            medical_history TEXT,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """

        try:
            self.execute_query(users_table)
            self.execute_query(patients_table)
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
