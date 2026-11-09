import sqlite3
import uuid

from core.database import get_connection
from core.logger import get_logger

log = get_logger("bundles.maintenance.models")


def report_maintenance(equipment_id, reported_by, issue_description,
                       reported_date):
    """Report a new maintenance issue for an equipment item.

    Inserts a maintenance record with Status='Under Maintenance' and updates
    the equipment status to 'Under Maintenance' within a single transaction.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    log.info("Maintenance reported: equipment=%s by=%s", equipment_id[:8], reported_by[:8])
    conn = get_connection()
    try:
        maintenance_id = str(uuid.uuid4())
        conn.execute("BEGIN")
        conn.execute(
            """INSERT INTO Maintenance
               (MaintenanceID, EquipmentID, ReportedBy, IssueDescription,
                ReportedDate, Status)
               VALUES (?, ?, ?, ?, ?, 'Under Maintenance')""",
            (maintenance_id, equipment_id, reported_by, issue_description,
             reported_date),
        )
        conn.execute(
            "UPDATE Equipment SET Status = 'Under Maintenance' WHERE EquipmentID = ?",
            (equipment_id,),
        )
        conn.commit()
        log.info("Maintenance record created: %s", maintenance_id[:8])
        return True, "Maintenance reported successfully."
    except sqlite3.Error as e:
        conn.rollback()
        log.error("Database error: %s", e)
        return False, f"Error reporting maintenance: {e}"
    finally:
        conn.close()


def complete_maintenance(maintenance_id, completed_date, remarks):
    """Mark a maintenance record as completed.

    Gets the EquipmentID from the maintenance record, then updates the
    maintenance record (CompletedDate, Remarks, Status='Completed') and
    sets the equipment status back to 'Available' within a single transaction.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    conn = get_connection()
    try:
        # Get EquipmentID from the maintenance record
        row = conn.execute(
            "SELECT EquipmentID FROM Maintenance WHERE MaintenanceID = ?",
            (maintenance_id,),
        ).fetchone()
        if not row:
            log.warning("Complete maintenance failed: record not found %s", maintenance_id[:8])
            return False, "Maintenance record not found."

        equipment_id = row["EquipmentID"]

        conn.execute("BEGIN")
        conn.execute(
            """UPDATE Maintenance
               SET CompletedDate = ?, Remarks = ?, Status = 'Completed'
               WHERE MaintenanceID = ?""",
            (completed_date, remarks, maintenance_id),
        )
        conn.execute(
            "UPDATE Equipment SET Status = 'Available' WHERE EquipmentID = ?",
            (equipment_id,),
        )
        conn.commit()
        log.info("Maintenance completed: %s equipment=%s", maintenance_id[:8], equipment_id[:8])
        return True, "Maintenance completed successfully."
    except sqlite3.Error as e:
        conn.rollback()
        log.error("Database error: %s", e)
        return False, f"Error completing maintenance: {e}"
    finally:
        conn.close()


def get_pending_maintenance():
    """Return a list of dicts for all pending maintenance records.

    Joins Equipment and Users tables. Ordered by ReportedDate DESC.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT m.MaintenanceID, m.EquipmentID, e.Name AS EquipmentName,
                      m.IssueDescription, u.FullName AS ReportedByName,
                      m.ReportedDate, m.Status
               FROM Maintenance m
               JOIN Equipment e ON m.EquipmentID = e.EquipmentID
               JOIN Users u ON m.ReportedBy = u.UserID
               WHERE m.Status = 'Under Maintenance'
               ORDER BY m.ReportedDate DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_maintenance():
    """Return a list of dicts for all maintenance records.

    Joins Equipment and Users tables. Ordered by ReportedDate DESC.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT m.MaintenanceID, m.EquipmentID, e.Name AS EquipmentName,
                      m.IssueDescription, u.FullName AS ReportedByName,
                      m.ReportedDate, m.CompletedDate, m.Remarks, m.Status
               FROM Maintenance m
               JOIN Equipment e ON m.EquipmentID = e.EquipmentID
               JOIN Users u ON m.ReportedBy = u.UserID
               ORDER BY m.ReportedDate DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
