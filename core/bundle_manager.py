import importlib
import os

from core.database import get_connection
from core.logger import get_logger

log = get_logger("core.bundle_manager")


class BundleManager:
    """Discovers, loads, and manages bundles from the bundles/ directory."""

    def __init__(self):
        self._bundles = {}      # name -> bundle_instance
        self._load_order = []   # ordered list of bundle names

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover_bundles(self):
        """Scan the bundles/ directory. Each subfolder with __init__.py that
        has a 'bundle' attribute (instance of BaseBundle) is registered."""
        bundles_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "bundles"
        )
        log.info("Discovering bundles in %s", bundles_dir)
        for name in sorted(os.listdir(bundles_dir)):
            pkg_dir = os.path.join(bundles_dir, name)
            if os.path.isdir(pkg_dir) and os.path.exists(
                os.path.join(pkg_dir, "__init__.py")
            ):
                try:
                    module = importlib.import_module(f"bundles.{name}")
                    if hasattr(module, "bundle"):
                        self._bundles[module.bundle.name] = module.bundle
                        log.info("Loaded bundle: %s v%s", module.bundle.name, module.bundle.version)
                except Exception as e:
                    log.warning("Failed to load bundle '%s': %s", name, e)

        # Resolve load order based on depends_on (simple topological sort)
        self._resolve_load_order()

    def _resolve_load_order(self):
        """Simple topological sort based on depends_on."""
        visited = set()
        order = []

        def visit(name):
            if name in visited:
                return
            visited.add(name)
            b = self._bundles.get(name)
            if b:
                for dep in b.depends_on:
                    visit(dep)
                order.append(name)

        for name in self._bundles:
            visit(name)
        self._load_order = order
        log.info("Bundle load order: %s", self._load_order)

    # ------------------------------------------------------------------
    # Database initialisation
    # ------------------------------------------------------------------

    def initialize_database(self):
        """Create tables and indexes for all bundles, seed data if empty."""
        log.info("Initializing database for %d bundles", len(self._load_order))
        conn = get_connection()
        cursor = conn.cursor()

        for name in self._load_order:
            log.debug("Creating tables for bundle: %s", name)
            b = self._bundles[name]
            for sql in b.get_tables_sql():
                cursor.executescript(sql)
            for sql in b.get_indexes_sql():
                cursor.execute(sql)

        conn.commit()

        # Migrations: add CreatedAt column to existing tables if missing
        for table in ("Users", "Category"):
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN CreatedAt DATETIME")
                conn.commit()
                log.info("Added CreatedAt column to %s", table)
            except Exception:
                pass  # column already exists

        # Seed data -- check each bundle's first table
        for name in self._load_order:
            b = self._bundles[name]
            seed_data = b.get_seed_data_sql()
            if seed_data:
                # Check if first table has data by trying the first INSERT
                first_sql = seed_data[0][0]
                # Extract table name from INSERT INTO TableName ...
                table_name = first_sql.split("INTO")[1].split("(")[0].strip()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                if cursor.fetchone()[0] == 0:
                    log.info("Seeding data for bundle: %s", name)
                    for sql, params_list in seed_data:
                        cursor.executemany(sql, params_list)

        conn.commit()
        conn.close()
        log.info("Database initialization complete")

    # ------------------------------------------------------------------
    # Tab collection helpers
    # ------------------------------------------------------------------

    def get_staff_tabs(self, parent, current_user):
        """Collect all staff tabs from all bundles in load order."""
        tabs = []
        for name in self._load_order:
            tabs.extend(self._bundles[name].get_staff_tabs(parent, current_user))
        return tabs

    def get_student_tabs(self, parent, current_user):
        """Collect all student tabs from all bundles in load order."""
        tabs = []
        for name in self._load_order:
            tabs.extend(
                self._bundles[name].get_student_tabs(parent, current_user)
            )
        return tabs

    def get_admin_tabs(self, parent, current_user):
        """Collect admin-only tabs from all bundles."""
        tabs = []
        for name in self._load_order:
            tabs.extend(
                self._bundles[name].get_admin_tabs(parent, current_user)
            )
        return tabs

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_bundle(self, name):
        """Get a bundle instance by name."""
        return self._bundles.get(name)

    @property
    def bundles(self):
        return self._bundles
