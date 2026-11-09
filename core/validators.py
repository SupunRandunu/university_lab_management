import re
from datetime import datetime


def validate_not_empty(value, field_name):
    """Check that *value* is not empty or whitespace-only.

    Returns:
        (bool, str): (True, "") on success or (False, error_message).
    """
    if not value or not str(value).strip():
        return False, f"{field_name} cannot be empty."
    return True, ""


def validate_date_format(date_str):
    """Check that *date_str* matches YYYY-MM-DD and is a valid calendar date.

    Returns:
        (bool, str): (True, "") on success or (False, error_message).
    """
    if not date_str or not date_str.strip():
        return False, "Date cannot be empty."
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format."


def validate_time_format(time_str):
    """Check that *time_str* matches HH:MM (24-hour).

    Returns:
        (bool, str): (True, "") on success or (False, error_message).
    """
    if not time_str or not time_str.strip():
        return False, "Time cannot be empty."
    if not re.match(r"^\d{2}:\d{2}$", time_str.strip()):
        return False, "Time must be in HH:MM format."
    try:
        parts = time_str.strip().split(":")
        hour, minute = int(parts[0]), int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return False, "Time must be in HH:MM format with valid hours (00-23) and minutes (00-59)."
        return True, ""
    except ValueError:
        return False, "Time must be in HH:MM format."


def validate_time_range(start, end):
    """Check that *start* time is strictly before *end* time (both HH:MM).

    Returns:
        (bool, str): (True, "") on success or (False, error_message).
    """
    ok, msg = validate_time_format(start)
    if not ok:
        return False, f"Start time error: {msg}"
    ok, msg = validate_time_format(end)
    if not ok:
        return False, f"End time error: {msg}"

    start_parts = start.strip().split(":")
    end_parts = end.strip().split(":")
    start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
    end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])

    if start_minutes >= end_minutes:
        return False, "Start time must be before end time."
    return True, ""


def validate_email(email):
    """Basic email validation. The field is optional -- empty is accepted.

    Returns:
        (bool, str): (True, "") on success or (False, error_message).
    """
    if not email or not email.strip():
        # Optional field; empty is fine
        return True, ""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email.strip()):
        return False, "Invalid email format."
    return True, ""


def validate_equipment_id(eq_id):
    """Check that *eq_id* is not empty and at most 10 characters.

    Returns:
        (bool, str): (True, "") on success or (False, error_message).
    """
    if not eq_id or not str(eq_id).strip():
        return False, "Equipment ID cannot be empty."
    if len(str(eq_id).strip()) > 10:
        return False, "Equipment ID must be at most 10 characters."
    return True, ""
