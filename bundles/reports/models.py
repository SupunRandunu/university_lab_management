from core.database import get_connection

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None


def generate_pdf(title, headers, data, filename):
    """Generate a landscape-A4 PDF report with the given data.

    Args:
        title: Report title printed at the top.
        headers: List of column header strings.
        data: List of row tuples/lists.
        filename: Destination file path.

    Returns:
        The filename on success.
    """
    if FPDF is None:
        raise ImportError("fpdf2 is required for PDF export. Install with: pip install fpdf2")

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(5)

    page_width = pdf.w - 2 * pdf.l_margin
    col_width = page_width / len(headers)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(200, 200, 200)
    for h in headers:
        pdf.cell(col_width, 8, str(h), border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    for row in data:
        for val in row:
            text = str(val) if val is not None else ""
            if len(text) > 30:
                text = text[:27] + "..."
            pdf.cell(col_width, 7, text, border=1, align="C")
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 8)
    from datetime import datetime
    pdf.cell(0, 5,
             f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
             align="R")

    pdf.output(filename)
    return filename


def get_equipment_report(from_date, to_date):
    """Equipment purchased within the given date range.

    Returns a list of dicts with keys:
    EquipmentID, Name, Category, LabName, PurchaseDate, Status.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT e.EquipmentID, e.Name, e.Category,
                      l.LabName, e.PurchaseDate, e.Status
               FROM Equipment e
               LEFT JOIN Laboratory l ON e.LabID = l.LabID
               WHERE e.PurchaseDate BETWEEN ? AND ?
               ORDER BY e.PurchaseDate DESC""",
            (from_date, to_date),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_borrowing_report(from_date, to_date):
    """Borrowing records where BorrowDate falls within the given range.

    Returns a list of dicts with keys:
    BorrowID, StudentName, EquipmentName, BorrowDate, DueDate,
    ReturnDate, ReturnCondition.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT b.BorrowID, u.FullName AS StudentName,
                      e.Name AS EquipmentName,
                      b.BorrowDate, b.DueDate, b.ReturnDate,
                      b.ReturnCondition
               FROM Borrowing b
               JOIN Users u ON b.UserID = u.UserID
               JOIN Equipment e ON b.EquipmentID = e.EquipmentID
               WHERE b.BorrowDate BETWEEN ? AND ?
               ORDER BY b.BorrowDate DESC""",
            (from_date, to_date),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_returning_report(from_date, to_date):
    """Returned borrowing records where ReturnDate falls within the given range.

    Returns a list of dicts with keys:
    BorrowID, StudentName, EquipmentName, BorrowDate, DueDate,
    ReturnDate, ReturnCondition.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT b.BorrowID, u.FullName AS StudentName,
                      e.Name AS EquipmentName,
                      b.BorrowDate, b.DueDate, b.ReturnDate,
                      b.ReturnCondition
               FROM Borrowing b
               JOIN Users u ON b.UserID = u.UserID
               JOIN Equipment e ON b.EquipmentID = e.EquipmentID
               WHERE b.ReturnDate IS NOT NULL
                 AND b.ReturnDate BETWEEN ? AND ?
               ORDER BY b.ReturnDate DESC""",
            (from_date, to_date),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_booking_report(from_date, to_date):
    """Booking records where BookingDate falls within the given range.

    Returns a list of dicts with keys:
    BookingID, StudentName, LabName, BookingDate, StartTime, EndTime,
    Purpose, Status.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT bk.BookingID, u.FullName AS StudentName,
                      l.LabName, bk.BookingDate, bk.StartTime, bk.EndTime,
                      bk.Purpose, bk.Status
               FROM Booking bk
               JOIN Users u ON bk.UserID = u.UserID
               JOIN Laboratory l ON bk.LabID = l.LabID
               WHERE bk.BookingDate BETWEEN ? AND ?
               ORDER BY bk.BookingDate DESC""",
            (from_date, to_date),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_maintenance_report(from_date, to_date):
    """Maintenance records where ReportedDate falls within the given range.

    Returns a list of dicts with keys:
    MaintenanceID, EquipmentName, IssueDescription, ReportedByName,
    ReportedDate, CompletedDate, Remarks, Status.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT m.MaintenanceID, e.Name AS EquipmentName,
                      m.IssueDescription, u.FullName AS ReportedByName,
                      m.ReportedDate, m.CompletedDate, m.Remarks, m.Status
               FROM Maintenance m
               JOIN Equipment e ON m.EquipmentID = e.EquipmentID
               JOIN Users u ON m.ReportedBy = u.UserID
               WHERE m.ReportedDate BETWEEN ? AND ?
               ORDER BY m.ReportedDate DESC""",
            (from_date, to_date),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
