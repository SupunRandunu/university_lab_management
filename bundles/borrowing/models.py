import sqlite3
import uuid

from core.database import get_connection
from core.logger import get_logger

log = get_logger("bundles.borrowing.models")


def borrow_equipment(user_id, equipment_id, issued_by, borrow_date, due_date):
    """Issue equipment to a student.

    Checks that the user is a Student and the equipment is Available,
    then inserts a borrowing record and sets equipment status to 'Borrowed'.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    log.info("Borrowing: student=%s equipment=%s issued_by=%s", user_id[:8], equipment_id[:8], issued_by[:8])
    conn = get_connection()
    try:
        # Check student exists with Role='Student'
        student = conn.execute(
            "SELECT 1 FROM Users WHERE UserID = ? AND Role = 'Student'",
            (user_id,),
        ).fetchone()
        if not student:
            msg = "Student not found or user is not a student."
            log.warning("Borrow failed: %s", msg)
            return False, msg

        # Check equipment is Available
        equipment = conn.execute(
            "SELECT Status FROM Equipment WHERE EquipmentID = ?",
            (equipment_id,),
        ).fetchone()
        if not equipment:
            msg = "Equipment not found."
            log.warning("Borrow failed: %s", msg)
            return False, msg
        if equipment["Status"] != "Available":
            msg = f"Equipment is not available (current status: {equipment['Status']})."
            log.warning("Borrow failed: %s", msg)
            return False, msg

        # BEGIN transaction
        borrow_id = str(uuid.uuid4())
        conn.execute("BEGIN")
        conn.execute(
            """INSERT INTO Borrowing
               (BorrowID, UserID, EquipmentID, IssuedBy, BorrowDate, DueDate)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (borrow_id, user_id, equipment_id, issued_by, borrow_date,
             due_date),
        )
        conn.execute(
            "UPDATE Equipment SET Status = 'Borrowed' WHERE EquipmentID = ?",
            (equipment_id,),
        )
        conn.commit()
        log.info("Equipment borrowed successfully: %s", equipment_id[:8])
        return True, "Equipment issued successfully."
    except sqlite3.Error as e:
        conn.rollback()
        log.error("Database error: %s", e)
        return False, f"Database error: {e}"
    finally:
        conn.close()


def return_equipment(equipment_id, return_date, is_damaged, staff_id):
    """Return borrowed equipment.

    Finds the active borrowing record (ReturnDate IS NULL) for the equipment,
    updates it with the return date and condition, and sets the equipment
    status accordingly. If damaged, also creates a Maintenance record.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    log.info("Returning equipment: %s (damaged=%s)", equipment_id[:8], is_damaged)
    conn = get_connection()
    try:
        # Find active borrowing record
        row = conn.execute(
            """SELECT BorrowID FROM Borrowing
               WHERE EquipmentID = ? AND ReturnDate IS NULL""",
            (equipment_id,),
        ).fetchone()
        if not row:
            msg = "No active borrowing found for this equipment."
            log.warning("Return failed: %s", msg)
            return False, msg

        borrow_id = row["BorrowID"]
        condition = "Damaged" if is_damaged else "Good"
        new_status = "Under Maintenance" if is_damaged else "Available"

        # BEGIN transaction
        conn.execute("BEGIN")

        # Update borrowing record
        conn.execute(
            """UPDATE Borrowing
               SET ReturnDate = ?, ReturnCondition = ?
               WHERE BorrowID = ?""",
            (return_date, condition, borrow_id),
        )

        # Update equipment status
        conn.execute(
            "UPDATE Equipment SET Status = ? WHERE EquipmentID = ?",
            (new_status, equipment_id),
        )

        # If damaged, insert a Maintenance record (Fix #5)
        if is_damaged:
            maintenance_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO Maintenance
                   (MaintenanceID, EquipmentID, IssueDescription, ReportedBy,
                    ReportedDate, Status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (maintenance_id, equipment_id,
                 "Returned in damaged condition",
                 staff_id, return_date, "Under Maintenance"),
            )
            log.info("Auto-created maintenance record for damaged equipment: %s", equipment_id[:8])

        conn.commit()
        log.info("Equipment returned: %s condition=%s", equipment_id[:8], condition)
        return True, "Equipment returned successfully."
    except sqlite3.Error as e:
        conn.rollback()
        log.error("Database error: %s", e)
        return False, f"Database error: {e}"
    finally:
        conn.close()


def get_active_borrow(equipment_id):
    """Return the active borrowing record for an equipment, or None.

    Joins with Users to include the student's full name as StudentName.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT b.BorrowID, b.UserID, b.EquipmentID, b.IssuedBy,
                      b.BorrowDate, b.DueDate, b.ReturnDate,
                      b.ReturnCondition,
                      u.FullName AS StudentName
               FROM Borrowing b
               JOIN Users u ON b.UserID = u.UserID
               WHERE b.EquipmentID = ? AND b.ReturnDate IS NULL""",
            (equipment_id,),
        ).fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_all_borrowings():
    """Return all borrowing records with student, issuer, and equipment info.

    Results are ordered by BorrowDate descending.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT b.BorrowID, b.UserID, b.EquipmentID, b.IssuedBy,
                      b.BorrowDate, b.DueDate, b.ReturnDate,
                      b.ReturnCondition,
                      u.FullName AS StudentName,
                      staff.FullName AS IssuedByName,
                      e.Name AS EquipmentName
               FROM Borrowing b
               JOIN Users u ON b.UserID = u.UserID
               JOIN Users staff ON b.IssuedBy = staff.UserID
               JOIN Equipment e ON b.EquipmentID = e.EquipmentID
               ORDER BY b.BorrowDate DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_active_borrowings():
    """Return active borrowing records (ReturnDate IS NULL).

    Joins with Users and Equipment for display information.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT b.BorrowID, b.UserID, b.EquipmentID, b.IssuedBy,
                      b.BorrowDate, b.DueDate, b.ReturnDate,
                      b.ReturnCondition,
                      u.FullName AS StudentName,
                      staff.FullName AS IssuedByName,
                      e.Name AS EquipmentName
               FROM Borrowing b
               JOIN Users u ON b.UserID = u.UserID
               JOIN Users staff ON b.IssuedBy = staff.UserID
               JOIN Equipment e ON b.EquipmentID = e.EquipmentID
               WHERE b.ReturnDate IS NULL
               ORDER BY b.BorrowDate DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
