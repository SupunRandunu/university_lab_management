from core.base_bundle import BaseBundle


class MaintenanceBundle(BaseBundle):
    name = "maintenance"
    label = "Maintenance Management"
    version = "1.0.0"
    depends_on = ["user_management", "equipment"]

    def get_tables_sql(self):
        return [
            """
            CREATE TABLE IF NOT EXISTS Maintenance (
                MaintenanceID TEXT PRIMARY KEY,
                EquipmentID TEXT NOT NULL,
                ReportedBy TEXT NOT NULL,
                IssueDescription VARCHAR(255),
                ReportedDate DATE NOT NULL,
                CompletedDate DATE,
                Remarks VARCHAR(255),
                Status VARCHAR(20) NOT NULL DEFAULT 'Under Maintenance'
                    CHECK(Status IN ('Under Maintenance', 'Completed')),
                FOREIGN KEY (EquipmentID) REFERENCES Equipment(EquipmentID),
                FOREIGN KEY (ReportedBy) REFERENCES Users(UserID)
            )
            """,
        ]

    def get_indexes_sql(self):
        return [
            "CREATE INDEX IF NOT EXISTS idx_maintenance_equipment ON Maintenance(EquipmentID)",
            "CREATE INDEX IF NOT EXISTS idx_maintenance_status ON Maintenance(Status)",
            "CREATE INDEX IF NOT EXISTS idx_maintenance_reported_date ON Maintenance(ReportedDate)",
        ]

    def get_seed_data_sql(self):
        return []

    def get_staff_tabs(self, parent, current_user):
        from bundles.maintenance.views import MaintenanceFrame
        return [
            ("Maintenance", MaintenanceFrame(parent, current_user)),
        ]


bundle = MaintenanceBundle()
