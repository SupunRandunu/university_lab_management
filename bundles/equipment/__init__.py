import uuid

from core.base_bundle import BaseBundle

# Generate lab UUIDs once so equipment seed data can reference them
LAB_IDS = [str(uuid.uuid4()) for _ in range(3)]

# Generate category UUIDs for seed data
CAT_IDS = [str(uuid.uuid4()) for _ in range(8)]


class EquipmentBundle(BaseBundle):
    name = "equipment"
    label = "Equipment Management"
    version = "1.0.0"
    depends_on = ["user_management"]

    def get_tables_sql(self):
        return [
            """
            CREATE TABLE IF NOT EXISTS Category (
                CategoryID TEXT PRIMARY KEY,
                CategoryName VARCHAR(100) NOT NULL UNIQUE,
                Description VARCHAR(255),
                CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Laboratory (
                LabID TEXT PRIMARY KEY,
                LabName VARCHAR(100) NOT NULL,
                Location VARCHAR(100),
                Capacity INTEGER
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Equipment (
                EquipmentID TEXT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Category VARCHAR(50),
                LabID TEXT,
                PurchaseDate DATE,
                Status VARCHAR(20) NOT NULL DEFAULT 'Available'
                    CHECK(Status IN ('Available', 'Borrowed', 'Under Maintenance')),
                FOREIGN KEY (LabID) REFERENCES Laboratory(LabID)
            )
            """,
        ]

    def get_indexes_sql(self):
        return [
            "CREATE INDEX IF NOT EXISTS idx_equipment_name ON Equipment(Name)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_category ON Equipment(Category)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_status ON Equipment(Status)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_lab ON Equipment(LabID)",
            "CREATE INDEX IF NOT EXISTS idx_category_name ON Category(CategoryName)",
        ]

    def get_seed_data_sql(self):
        cat_sql = """
            INSERT OR IGNORE INTO Category (CategoryID, CategoryName, Description)
            VALUES (?, ?, ?)
        """
        cat_data = [
            (CAT_IDS[0], "Computer", "Desktop computers and workstations"),
            (CAT_IDS[1], "Laptop", "Portable laptop computers"),
            (CAT_IDS[2], "Switch", "Network switches and hubs"),
            (CAT_IDS[3], "Measuring Instrument", "Multimeters, calipers, and other measuring tools"),
            (CAT_IDS[4], "Oscilloscope", "Signal measuring oscilloscopes"),
            (CAT_IDS[5], "Microcontroller", "Arduino, ESP32, and microcontroller kits"),
            (CAT_IDS[6], "Single Board Computer", "Raspberry Pi and similar SBCs"),
            (CAT_IDS[7], "Router", "Network routers and access points"),
        ]

        lab_sql = """
            INSERT OR IGNORE INTO Laboratory (LabID, LabName, Location, Capacity)
            VALUES (?, ?, ?, ?)
        """
        lab_data = [
            (LAB_IDS[0], "Computer Lab A", "Building C, Room 101", 40),
            (LAB_IDS[1], "Electronics Lab", "Building D, Room 203", 30),
            (LAB_IDS[2], "Networking Lab", "Building C, Room 305", 25),
        ]

        eq_sql = """
            INSERT OR IGNORE INTO Equipment
                (EquipmentID, Name, Category, LabID, PurchaseDate, Status)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        eq_data = [
            (str(uuid.uuid4()), "Dell OptiPlex 7090", "Computer", LAB_IDS[0],
             "2024-03-15", "Available"),
            (str(uuid.uuid4()), "HP ProBook 450", "Laptop", LAB_IDS[0],
             "2024-06-20", "Available"),
            (str(uuid.uuid4()), "Cisco Catalyst 2960", "Switch", LAB_IDS[2],
             "2023-11-10", "Available"),
            (str(uuid.uuid4()), "Fluke 87V Multimeter", "Measuring Instrument",
             LAB_IDS[1], "2024-01-05", "Available"),
            (str(uuid.uuid4()), "Tektronix TBS1052C", "Oscilloscope",
             LAB_IDS[1], "2023-08-22", "Borrowed"),
            (str(uuid.uuid4()), "Arduino Uno R3 Kit", "Microcontroller",
             LAB_IDS[1], "2024-09-01", "Available"),
            (str(uuid.uuid4()), "TP-Link TL-SG108", "Switch", LAB_IDS[2],
             "2024-04-18", "Under Maintenance"),
            (str(uuid.uuid4()), "Raspberry Pi 4 Model B", "Single Board Computer",
             LAB_IDS[0], "2024-07-30", "Available"),
        ]

        return [(cat_sql, cat_data), (lab_sql, lab_data), (eq_sql, eq_data)]

    def get_staff_tabs(self, parent, current_user):
        from bundles.equipment.views import (
            EquipmentManagementFrame,
            EquipmentSearchFrame,
        )
        return [
            ("Equipment Management",
             EquipmentManagementFrame(parent, current_user)),
            ("Search Equipment",
             EquipmentSearchFrame(parent, current_user)),
        ]

    def get_student_tabs(self, parent, current_user):
        from bundles.equipment.views import EquipmentSearchFrame
        return [
            ("Search Equipment",
             EquipmentSearchFrame(parent, current_user)),
        ]

    def get_admin_tabs(self, parent, current_user):
        from bundles.equipment.views import CategoryManagementFrame
        return [
            ("Manage Categories",
             CategoryManagementFrame(parent, current_user)),
        ]


bundle = EquipmentBundle()
