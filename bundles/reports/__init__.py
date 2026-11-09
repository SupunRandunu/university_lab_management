from core.base_bundle import BaseBundle


class ReportsBundle(BaseBundle):
    name = "reports"
    label = "Reports"
    version = "1.0.0"
    depends_on = ["user_management", "equipment", "borrowing", "booking",
                  "maintenance"]

    # No tables -- this bundle reads from other bundles' tables.

    def get_staff_tabs(self, parent, current_user):
        from bundles.reports.views import ReportFrame
        return [
            ("Reports", ReportFrame(parent, current_user)),
        ]


bundle = ReportsBundle()
