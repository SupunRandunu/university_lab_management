from core.base_bundle import BaseBundle
from core.auth import hash_password
import uuid


class UserManagementBundle(BaseBundle):
    name = "user_management"
    label = "User Management"
    version = "1.0.0"
    depends_on = []

    def get_tables_sql(self):
        return [
            """
            CREATE TABLE IF NOT EXISTS Users (
                UserID TEXT PRIMARY KEY,
                FullName VARCHAR(100) NOT NULL,
                Username VARCHAR(50) NOT NULL,
                PasswordHash VARCHAR(255) NOT NULL,
                Role VARCHAR(20) NOT NULL CHECK(Role IN ('Student', 'Staff', 'Admin')),
                IndexNo VARCHAR(20),
                Email VARCHAR(100) UNIQUE NOT NULL,
                ContactNo VARCHAR(15),
                CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]

    def get_indexes_sql(self):
        return [
            "CREATE INDEX IF NOT EXISTS idx_users_email ON Users(Email)",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON Users(Username)"
        ]

    def get_seed_data_sql(self):
        sql = """
            INSERT OR IGNORE INTO Users
                (UserID, FullName, Username, PasswordHash, Role, IndexNo, Email, ContactNo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        data = [
            (str(uuid.uuid4()), "Admin User", "admin", hash_password("admin123"),
             "Admin", None, "admin@uom.lk", None),
            (str(uuid.uuid4()), "John Smith", "john", hash_password("staff123"),
             "Staff", None, "john.smith@uom.lk", "0771234567"),
            (str(uuid.uuid4()), "Sarah Johnson", "sarah", hash_password("staff456"),
             "Staff", None, "sarah.j@uom.lk", "0772345678"),
            (str(uuid.uuid4()), "David Brown", "david", hash_password("student123"),
             "Student", "e2518045", "david.b@students.uom.lk", "0779876543"),
            (str(uuid.uuid4()), "Emma Wilson", "emma", hash_password("student456"),
             "Student", "e2518062", "emma.w@students.uom.lk", "0778765432"),
        ]
        return [(sql, data)]

    def get_admin_tabs(self, parent, current_user):
        from bundles.user_management.views import UserManagementFrame
        return [("User Management", UserManagementFrame(parent, current_user))]


bundle = UserManagementBundle()
