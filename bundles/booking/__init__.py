from core.base_bundle import BaseBundle


class BookingBundle(BaseBundle):
    name = "booking"
    label = "Laboratory Booking"
    version = "1.0.0"
    depends_on = ["user_management", "equipment"]

    def get_tables_sql(self):
        return [
            """
            CREATE TABLE IF NOT EXISTS Booking (
                BookingID TEXT PRIMARY KEY,
                UserID TEXT NOT NULL,
                LabID TEXT NOT NULL,
                BookingDate DATE NOT NULL,
                StartTime TIME NOT NULL,
                EndTime TIME NOT NULL,
                Purpose VARCHAR(200),
                Status VARCHAR(20) NOT NULL DEFAULT 'Pending'
                    CHECK(Status IN ('Pending', 'Approved', 'Rejected')),
                ApprovedBy TEXT,
                FOREIGN KEY (UserID) REFERENCES Users(UserID),
                FOREIGN KEY (LabID) REFERENCES Laboratory(LabID),
                FOREIGN KEY (ApprovedBy) REFERENCES Users(UserID)
            )
            """,
        ]

    def get_indexes_sql(self):
        return [
            "CREATE INDEX IF NOT EXISTS idx_booking_lab_date ON Booking(LabID, BookingDate)",
            "CREATE INDEX IF NOT EXISTS idx_booking_status ON Booking(Status)",
            "CREATE INDEX IF NOT EXISTS idx_booking_user ON Booking(UserID)",
        ]

    def get_seed_data_sql(self):
        return []

    def get_staff_tabs(self, parent, current_user):
        from bundles.booking.views import BookingStaffFrame
        return [
            ("Lab Bookings", BookingStaffFrame(parent, current_user)),
        ]

    def get_student_tabs(self, parent, current_user):
        from bundles.booking.views import BookingStudentFrame
        return [
            ("Lab Booking", BookingStudentFrame(parent, current_user)),
        ]


bundle = BookingBundle()
