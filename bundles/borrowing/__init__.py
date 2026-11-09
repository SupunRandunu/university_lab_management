from core.base_bundle import BaseBundle


class BorrowingBundle(BaseBundle):
    name = "borrowing"
    label = "Borrowing & Returning"
    version = "1.0.0"
    depends_on = ["user_management", "equipment"]

    def get_tables_sql(self):
        return [
            """
            CREATE TABLE IF NOT EXISTS Borrowing (
                BorrowID TEXT PRIMARY KEY,
                UserID TEXT NOT NULL,
                EquipmentID TEXT NOT NULL,
                IssuedBy TEXT NOT NULL,
                BorrowDate DATE NOT NULL,
                DueDate DATE NOT NULL,
                ReturnDate DATE,
                ReturnCondition VARCHAR(20)
                    CHECK(ReturnCondition IN ('Good', 'Damaged')),
                FOREIGN KEY (UserID) REFERENCES Users(UserID),
                FOREIGN KEY (EquipmentID) REFERENCES Equipment(EquipmentID),
                FOREIGN KEY (IssuedBy) REFERENCES Users(UserID)
            )
            """,
        ]

    def get_indexes_sql(self):
        return [
            "CREATE INDEX IF NOT EXISTS idx_borrowing_equipment ON Borrowing(EquipmentID)",
            "CREATE INDEX IF NOT EXISTS idx_borrowing_user ON Borrowing(UserID)",
            "CREATE INDEX IF NOT EXISTS idx_borrowing_return_date ON Borrowing(ReturnDate)",
            "CREATE INDEX IF NOT EXISTS idx_borrowing_borrow_date ON Borrowing(BorrowDate)",
        ]

    def get_seed_data_sql(self):
        return []

    def get_staff_tabs(self, parent, current_user):
        from bundles.borrowing.views import BorrowingFrame
        return [
            ("Borrowing & Returning",
             BorrowingFrame(parent, current_user)),
        ]


bundle = BorrowingBundle()
