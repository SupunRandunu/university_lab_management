import uuid

from core.database import get_connection
from core.logger import get_logger

log = get_logger("bundles.booking.models")


def create_booking(user_id, lab_id, booking_date, start_time, end_time,
                   purpose):
    """Create a new booking after checking for time-slot overlaps.

    Overlap is checked against both Pending and Approved bookings so that
    a slot already requested (but not yet approved) is still blocked.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    log.info("Booking request: user=%s lab=%s date=%s %s-%s", user_id[:8], lab_id[:8], booking_date, start_time, end_time)
    conn = get_connection()
    try:
        # FIX #1: check overlap against BOTH Pending AND Approved bookings
        row = conn.execute(
            """SELECT COUNT(*) AS cnt FROM Booking
               WHERE LabID = ? AND BookingDate = ?
                 AND Status IN ('Pending', 'Approved')
                 AND StartTime < ? AND EndTime > ?""",
            (lab_id, booking_date, end_time, start_time),
        ).fetchone()

        if row and row["cnt"] > 0:
            log.warning("Booking rejected - slot not available")
            return False, "Slot not available"

        booking_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO Booking
               (BookingID, UserID, LabID, BookingDate, StartTime, EndTime,
                Purpose, Status)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')""",
            (booking_id, user_id, lab_id, booking_date, start_time, end_time,
             purpose),
        )
        conn.commit()
        log.info("Booking created: %s", booking_id[:8])
        return True, "Booking submitted successfully."
    except Exception as e:
        log.error("Database error: %s", e)
        return False, str(e)
    finally:
        conn.close()


def get_pending_bookings():
    """Return all pending bookings as a list of dicts.

    Includes StudentName (from Users) and LabName (from Laboratory).
    Ordered by BookingDate then StartTime.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT b.BookingID, u.FullName AS StudentName,
                      l.LabName, b.BookingDate, b.StartTime, b.EndTime,
                      b.Purpose, b.Status
               FROM Booking b
               JOIN Users u ON b.UserID = u.UserID
               JOIN Laboratory l ON b.LabID = l.LabID
               WHERE b.Status = 'Pending'
               ORDER BY b.BookingDate DESC, b.StartTime DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def approve_booking(booking_id, approved_by):
    """Approve a booking by setting Status to 'Approved'.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            """UPDATE Booking
               SET Status = 'Approved', ApprovedBy = ?
               WHERE BookingID = ?""",
            (approved_by, booking_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            log.warning("Approve booking failed: booking not found %s", booking_id[:8])
            return False, "Booking not found."
        log.info("Booking approved: %s by %s", booking_id[:8], approved_by[:8])
        return True, "Booking approved successfully."
    finally:
        conn.close()


def reject_booking(booking_id, approved_by):
    """Reject a booking by setting Status to 'Rejected'.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            """UPDATE Booking
               SET Status = 'Rejected', ApprovedBy = ?
               WHERE BookingID = ?""",
            (approved_by, booking_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            log.warning("Reject booking failed: booking not found %s", booking_id[:8])
            return False, "Booking not found."
        log.info("Booking rejected: %s by %s", booking_id[:8], approved_by[:8])
        return True, "Booking rejected successfully."
    finally:
        conn.close()


def get_bookings_by_user(user_id):
    """Return all bookings for a specific user as a list of dicts.

    Includes LabName from Laboratory. Ordered by BookingDate descending.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT b.BookingID, l.LabName, b.BookingDate,
                      b.StartTime, b.EndTime, b.Purpose, b.Status
               FROM Booking b
               JOIN Laboratory l ON b.LabID = l.LabID
               WHERE b.UserID = ?
               ORDER BY b.BookingDate DESC""",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_bookings():
    """Return all bookings as a list of dicts.

    Includes StudentName (from Users) and LabName (from Laboratory).
    Ordered by BookingDate descending.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT b.BookingID, u.FullName AS StudentName,
                      l.LabName, b.BookingDate, b.StartTime, b.EndTime,
                      b.Purpose, b.Status
               FROM Booking b
               JOIN Users u ON b.UserID = u.UserID
               JOIN Laboratory l ON b.LabID = l.LabID
               ORDER BY b.BookingDate DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
