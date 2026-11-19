import os
import pyodbc

driver = os.getenv("DB_ODBC_DRIVER", "MySQL ODBC 9.7 Unicode Driver")
connection_string = (
    f"DRIVER={{{driver}}};"
    f"SERVER={os.getenv('DB_HOST', '192.168.1.15')};"
    f"PORT={os.getenv('DB_PORT', '3306')};"
    f"DATABASE={os.getenv('DB_NAME', 'his_db')};"
    f"UID={os.getenv('DB_USER', 'root')};"
    f"PWD={os.getenv('DB_PASSWORD', 'root')};"
)

try:
    with pyodbc.connect(connection_string, timeout=5) as conn:
        result = conn.cursor().execute("SELECT 1").fetchone()
        print("ODBC connection works; test result:", result[0])
except pyodbc.Error as e:
    print("ODBC connection failed:", e)