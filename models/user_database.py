import hashlib
from mysql.connector import Error
from models.database import get_connection


class UserDatabase:
    """Handles all user account operations: auth, creation, update, delete."""

    def __init__(self):
        self.db = get_connection()  # Use singleton connection

    def hash_password(self, password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, username, password):
        """Authenticate user credentials."""
        query = "SELECT * FROM users WHERE username = %s"
        cursor = self.db.execute_query(query, (username,))

        if cursor:
            result = cursor.fetchone()
            if result:
                if result[2] == self.hash_password(password):
                    update_query = "UPDATE users SET last_login = NOW() WHERE username = %s"
                    self.db.execute_query(update_query, (username,))
                    self.db.commit()
                    user_data = {
                        'id': result[0],
                        'username': result[1],
                        'password': result[2],
                        'role': result[3],
                        'created_date': str(result[4]),
                        'last_login': str(result[5]) if result[5] else None
                    }
                    return True, user_data

        return False, None

    def add_user(self, username, password, role="Staff"):
        """Add a new user."""
        check_query = "SELECT COUNT(*) FROM users WHERE username = %s"
        cursor = self.db.execute_query(check_query, (username,))

        if cursor and cursor.fetchone()[0] > 0:
            return False, "Username already exists"

        insert_query = """
        INSERT INTO users (username, password, role, created_date)
        VALUES (%s, %s, %s, NOW())
        """
        try:
            self.db.execute_query(insert_query, (username, self.hash_password(password), role))
            self.db.commit()
            return True, "User created successfully"
        except Error as e:
            return False, f"Error creating user: {e}"

    def get_all_users(self):
        """Get all users."""
        query = "SELECT * FROM users ORDER BY created_date DESC"
        cursor = self.db.execute_query(query)

        users = {}
        if cursor:
            for row in cursor.fetchall():
                users[row[1]] = {
                    'id': row[0],
                    'username': row[1],
                    'password': row[2],
                    'role': row[3],
                    'created_date': str(row[4]),
                    'last_login': str(row[5]) if row[5] else None
                }
        return users

    def get_user(self, username):
        """Retrieve a single user by username."""
        query = "SELECT * FROM users WHERE username = %s"
        cursor = self.db.execute_query(query, (username,))
        if cursor:
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'username': row[1],
                    'password': row[2],
                    'role': row[3],
                    'created_date': str(row[4]),
                    'last_login': str(row[5]) if row[5] else None
                }
        return None

    def update_user(self, username, role=None, password=None):
        """Update a user's role and/or password."""
        if role is None and password is None:
            return False

        fields = []
        params = []
        if role is not None:
            fields.append("role = %s")
            params.append(role)
        if password is not None:
            fields.append("password = %s")
            params.append(self.hash_password(password))

        params.append(username)
        query = f"UPDATE users SET {', '.join(fields)} WHERE username = %s"

        try:
            cursor = self.db.execute_query(query, tuple(params))
            if cursor and cursor.rowcount > 0:
                self.db.commit()
                return True
        except Error as e:
            print(f"Error updating user: {e}")
        return False

    def delete_user(self, username):
        """Delete a user account."""
        query = "DELETE FROM users WHERE username = %s"
        try:
            cursor = self.db.execute_query(query, (username,))
            if cursor and cursor.rowcount > 0:
                self.db.commit()
                return True
        except Error as e:
            print(f"Error deleting user: {e}")
        return False
