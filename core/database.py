import os
import sqlite3

from core.logger import get_logger

log = get_logger("core.database")

# Compute the path to laboratory.db in the project root (university_lab_management/)
# This file lives at core/database.py, so two levels up from __file__:
#   __file__        -> core/database.py
#   dirname once    -> core/
#   dirname twice   -> university_lab_management/
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "laboratory.db"
)


def get_connection():
    """Return a sqlite3.Connection to the laboratory database.

    The connection has:
    - row_factory set to sqlite3.Row (dict-like row access)
    - PRAGMA foreign_keys = ON (enforce FK constraints)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    log.debug("Database connection opened: %s", DB_PATH)
    return conn
