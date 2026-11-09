import sqlite3
import uuid

from core.database import get_connection
from core.auth import hash_password
from core.logger import get_logger

log = get_logger("bundles.user_management.models")


def authenticate(email, password):
    """Authenticate a user by email and password.

    Returns:
        dict with user data on success, or None on failure.
    """
    log.info("Login attempt: %s", email)
    pw_hash = hash_password(password)
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM Users WHERE Email = ? AND PasswordHash = ?",
            (email, pw_hash),
        ).fetchone()
        if row:
            user = dict(row)
            log.info("Login successful: %s (%s)", user["FullName"], user["Role"])
            return user
        log.warning("Login failed: %s", email)
        return None
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Return a single user dict by UserID, or None if not found."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM Users WHERE UserID = ?", (user_id,)
        ).fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_students():
    """Return a list of dicts for all users with Role='Student'."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM Users WHERE Role = 'Student' ORDER BY CreatedAt DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_users():
    """Return a list of dicts for all users."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM Users ORDER BY CreatedAt DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def user_exists(user_id):
    """Return True if a user with the given UserID exists."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT 1 FROM Users WHERE UserID = ?", (user_id,)
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def student_exists(user_id):
    """Return True if a Student with the given UserID exists."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT 1 FROM Users WHERE UserID = ? AND Role = 'Student'",
            (user_id,),
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def add_user(full_name, username, email, password, role, index_no=None, contact_no=None):
    """Insert a new user. Email is the login credential (must be unique).
    Username is stored but NOT used for login.

    Returns (True, message) or (False, message).
    """
    log.info("Adding user: %s (%s) email=%s", full_name, role, email)
    user_id = str(uuid.uuid4())
    pw_hash = hash_password(password)
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO Users
               (UserID, FullName, Username, PasswordHash, Role, IndexNo, Email, ContactNo, CreatedAt)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (user_id, full_name, username, pw_hash, role, index_no, email, contact_no),
        )
        conn.commit()
        log.info("User added: %s [%s]", full_name, user_id[:8])
        return True, "User added successfully."
    except sqlite3.IntegrityError:
        msg = "Email already exists."
        log.warning("Add user failed: %s", msg)
        return False, msg
    finally:
        conn.close()


def update_user(user_id, full_name, username, email, role, index_no=None, contact_no=None):
    """Update an existing user (does NOT update password).

    Returns (True, message) or (False, message).
    """
    log.info("Updating user: %s", user_id[:8])
    conn = get_connection()
    try:
        conn.execute(
            """UPDATE Users
               SET FullName = ?, Username = ?, Email = ?, Role = ?,
                   IndexNo = ?, ContactNo = ?
               WHERE UserID = ?""",
            (full_name, username, email, role, index_no, contact_no, user_id),
        )
        conn.commit()
        return True, "User updated successfully."
    except sqlite3.IntegrityError:
        msg = "Email already exists."
        log.warning("Update user failed: %s", msg)
        return False, msg
    finally:
        conn.close()


def reset_password(user_id, new_password):
    """Hash and set a new password for the given user.

    Returns (True, message) or (False, message).
    """
    log.info("Password reset for user: %s", user_id[:8])
    pw_hash = hash_password(new_password)
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE Users SET PasswordHash = ? WHERE UserID = ?",
            (pw_hash, user_id),
        )
        conn.commit()
        return True, "Password reset successfully."
    finally:
        conn.close()


def delete_user(user_id):
    """Delete a user after checking for active borrowings.

    Returns (True, message) or (False, message).
    """
    log.info("Deleting user: %s", user_id[:8])
    conn = get_connection()
    try:
        try:
            row = conn.execute(
                """SELECT COUNT(*) AS cnt FROM Borrowing
                   WHERE UserID = ? AND ReturnDate IS NULL""",
                (user_id,),
            ).fetchone()
            if row and row["cnt"] > 0:
                log.warning("Delete user blocked: %s has active borrowings", user_id[:8])
                return False, "Cannot delete user with active borrowings."
        except sqlite3.OperationalError:
            pass

        conn.execute("DELETE FROM Users WHERE UserID = ?", (user_id,))
        conn.commit()
        return True, "User deleted successfully."
    finally:
        conn.close()
