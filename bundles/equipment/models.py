import sqlite3
import uuid

from core.database import get_connection
from core.logger import get_logger

log = get_logger("bundles.equipment.models")


# ---------------------------------------------------------------------------
# Category helpers
# ---------------------------------------------------------------------------

def get_all_categories():
    """Return a list of dicts for all categories, ordered by name."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM Category ORDER BY CreatedAt DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_category_names():
    """Return a sorted list of category name strings."""
    return [c["CategoryName"] for c in get_all_categories()]


def add_category(name, description=None):
    """Insert a new category. Returns (bool, str)."""
    log.info("Adding category: %s", name)
    conn = get_connection()
    try:
        cat_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO Category (CategoryID, CategoryName, Description, CreatedAt) VALUES (?, ?, ?, datetime('now'))",
            (cat_id, name.strip(), (description or "").strip()),
        )
        conn.commit()
        log.info("Category added: %s [%s]", name, cat_id[:8])
        return True, "Category added successfully."
    except sqlite3.IntegrityError:
        return False, "Category name already exists."
    finally:
        conn.close()


def update_category(cat_id, name, description=None):
    """Update an existing category. Returns (bool, str)."""
    log.info("Updating category: %s", cat_id[:8])
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE Category SET CategoryName = ?, Description = ? WHERE CategoryID = ?",
            (name.strip(), (description or "").strip(), cat_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return False, "Category not found."
        return True, "Category updated successfully."
    except sqlite3.IntegrityError:
        return False, "Category name already exists."
    finally:
        conn.close()


def delete_category(cat_id):
    """Delete a category if not used by any equipment. Returns (bool, str)."""
    log.info("Deleting category: %s", cat_id[:8])
    conn = get_connection()
    try:
        # Check if any equipment uses this category
        row = conn.execute(
            """SELECT c.CategoryName FROM Category c
               WHERE c.CategoryID = ?""", (cat_id,)
        ).fetchone()
        if not row:
            return False, "Category not found."
        cat_name = row["CategoryName"]

        count = conn.execute(
            "SELECT COUNT(*) AS cnt FROM Equipment WHERE Category = ?",
            (cat_name,),
        ).fetchone()
        if count and count["cnt"] > 0:
            return False, f"Cannot delete: {count['cnt']} equipment item(s) use this category."

        conn.execute("DELETE FROM Category WHERE CategoryID = ?", (cat_id,))
        conn.commit()
        return True, "Category deleted successfully."
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Laboratory helpers
# ---------------------------------------------------------------------------

def get_all_laboratories():
    """Return a list of dicts for all laboratories."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM Laboratory ORDER BY LabName"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_laboratory_by_id(lab_id):
    """Return a single laboratory dict by LabID (TEXT/UUID), or None."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM Laboratory WHERE LabID = ?", (lab_id,)
        ).fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Equipment helpers
# ---------------------------------------------------------------------------

def add_equipment(name, category, lab_id, purchase_date,
                  status="Available"):
    """Insert a new equipment record with an auto-generated UUID.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    log.info("Adding equipment: %s (%s)", name, category)
    conn = get_connection()
    try:
        eq_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO Equipment
               (EquipmentID, Name, Category, LabID, PurchaseDate, Status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (eq_id, name, category, lab_id, purchase_date, status),
        )
        conn.commit()
        log.info("Equipment added: %s [%s]", name, eq_id[:8])
        return True, "Equipment added successfully."
    except sqlite3.IntegrityError:
        msg = "Failed to add equipment (integrity error)."
        log.warning("Add equipment failed: %s", msg)
        return False, msg
    finally:
        conn.close()


def update_equipment(eq_id, name, category, lab_id, purchase_date, status):
    """Update an existing equipment record.

    Args:
        eq_id: UUID string identifying the equipment.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    log.info("Updating equipment: %s", eq_id[:8])
    conn = get_connection()
    try:
        cursor = conn.execute(
            """UPDATE Equipment
               SET Name = ?, Category = ?, LabID = ?,
                   PurchaseDate = ?, Status = ?
               WHERE EquipmentID = ?""",
            (name, category, lab_id, purchase_date, status, eq_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            log.warning("Update equipment failed: equipment not found %s", eq_id[:8])
            return False, "Equipment not found."
        return True, "Equipment updated successfully."
    finally:
        conn.close()


def delete_equipment(eq_id):
    """Delete an equipment record after checking for active borrowings.

    Args:
        eq_id: UUID string identifying the equipment.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    log.info("Deleting equipment: %s", eq_id[:8])
    conn = get_connection()
    try:
        # Check for active borrowings (ReturnDate IS NULL)
        try:
            row = conn.execute(
                """SELECT COUNT(*) AS cnt FROM Borrowings
                   WHERE EquipmentID = ? AND ReturnDate IS NULL""",
                (eq_id,),
            ).fetchone()
            if row and row["cnt"] > 0:
                log.warning("Delete equipment blocked: %s has active borrowings", eq_id[:8])
                return False, "Cannot delete equipment with active borrowings."
        except sqlite3.OperationalError:
            # Borrowings table may not exist yet; safe to proceed
            pass

        conn.execute(
            "DELETE FROM Equipment WHERE EquipmentID = ?", (eq_id,)
        )
        conn.commit()
        return True, "Equipment deleted successfully."
    finally:
        conn.close()


def get_all_equipment():
    """Return a list of dicts for all equipment, including LabName.

    Results are ordered by Name.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT e.EquipmentID, e.Name, e.Category,
                      e.LabID, l.LabName, e.PurchaseDate, e.Status
               FROM Equipment e
               LEFT JOIN Laboratory l ON e.LabID = l.LabID
               ORDER BY e.PurchaseDate DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def search_equipment(search_text):
    """Search equipment by Name, EquipmentID, or Category.

    Returns a list of dicts including LabName via JOIN.
    Partial UUID search is supported via LIKE.
    """
    log.debug("Equipment search: '%s'", search_text)
    conn = get_connection()
    try:
        like = f"%{search_text}%"
        rows = conn.execute(
            """SELECT e.EquipmentID, e.Name, e.Category,
                      e.LabID, l.LabName, e.PurchaseDate, e.Status
               FROM Equipment e
               LEFT JOIN Laboratory l ON e.LabID = l.LabID
               WHERE e.Name LIKE ?
                  OR e.EquipmentID LIKE ?
                  OR e.Category LIKE ?
               ORDER BY e.PurchaseDate DESC""",
            (like, like, like),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_equipment_by_id(eq_id):
    """Return a single equipment dict by EquipmentID (UUID string), or None.

    Includes LabName from the Laboratory table.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT e.EquipmentID, e.Name, e.Category,
                      e.LabID, l.LabName, e.PurchaseDate, e.Status
               FROM Equipment e
               LEFT JOIN Laboratory l ON e.LabID = l.LabID
               WHERE e.EquipmentID = ?""",
            (eq_id,),
        ).fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def update_equipment_status(eq_id, status):
    """Update only the Status column for a given equipment.

    Args:
        eq_id: UUID string identifying the equipment.

    Returns True on success, False if the equipment was not found.
    """
    log.info("Equipment %s status -> %s", eq_id[:8], status)
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE Equipment SET Status = ? WHERE EquipmentID = ?",
            (status, eq_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            log.warning("Equipment status update failed: equipment not found %s", eq_id[:8])
        return cursor.rowcount > 0
    finally:
        conn.close()
