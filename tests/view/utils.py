from aiohttp_admin2.views import Admin
from aiohttp_admin2.views import DashboardView

__all__ = ["generate_new_admin_class", ]


def generate_new_admin_class():
    """
    we need to generate a new dashboard view for each `setup_admin` call.
    """
    class MockDashboard(DashboardView):
        pass

    class MockAdmin(Admin):
        dashboard_class = MockDashboard

    return MockAdmin
