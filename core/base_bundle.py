class BaseBundle:
    """Base class for all bundles. Subclass this in each bundle's __init__.py."""

    name = ""           # unique identifier e.g. "equipment"
    label = ""          # display name e.g. "Equipment Management"
    version = "1.0.0"
    depends_on = []     # list of bundle names this depends on

    def get_tables_sql(self):
        """Return list of CREATE TABLE IF NOT EXISTS SQL strings."""
        return []

    def get_indexes_sql(self):
        """Return list of CREATE INDEX IF NOT EXISTS SQL strings."""
        return []

    def get_seed_data_sql(self):
        """Return list of (sql, params_list) tuples for executemany seed data.

        Each tuple is (INSERT sql string, list of param tuples).
        Only called if tables are empty.
        """
        return []

    def get_staff_tabs(self, parent, current_user):
        """Return list of (tab_label, frame_instance) for the staff notebook.

        Return empty list if this bundle has no staff tabs.
        """
        return []

    def get_student_tabs(self, parent, current_user):
        """Return list of (tab_label, frame_instance) for the student notebook.

        Return empty list if this bundle has no student tabs.
        """
        return []

    def get_admin_tabs(self, parent, current_user):
        """Return list of (tab_label, frame_instance) for admin-only tabs.

        These appear in the staff window only for Admin users.
        """
        return []
