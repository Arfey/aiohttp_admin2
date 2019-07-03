from aiohttp_admin2 import Admin
from aiohttp_admin2.views.dashboard import DashboardView
import aiohttp_admin2


async def test_simple_setup_admin(app, aiohttp_client):
    """
    In this test we check default setup of admin.

    1. check good status code after call to the default admin's url
    2. check existing default text in response body
    """
    aiohttp_admin2.setup(app)

    client = await aiohttp_client(app)
    res = await client.get(Admin.prefix_url)

    # 1. check good status code after call to the default admin's the url
    assert res.status == 200

    # 2. check existing default text in response body
    assert Admin.name in await res.text()


async def test_setup_admin_with_custom_admin_class(app, aiohttp_client):
    """
    In this test we check that applied custom admin class.

    1. check good status code after call to the custom admin's url
    2. check existing custom title in response body
    3. check the custom index handler
    """
    class CustomAdmin(Admin):
        name = 'new text'
        prefix_url = '/new-url/'

    test_text = 'test_text'

    class CustomDashboardView(DashboardView):
        title = test_text

    class CustomIndexAdmin(Admin):
        dashboard_class = CustomDashboardView

    aiohttp_admin2.setup(app, admin_class=CustomAdmin)
    aiohttp_admin2.setup(app, admin_class=CustomIndexAdmin)
    client = await aiohttp_client(app)

    res = await client.get(CustomAdmin.prefix_url)

    # 1. check good status code after call to the custom admin's url
    assert res.status == 200

    # 2. check existing custom title in response body
    assert CustomAdmin.name in await res.text()

    # 3. check the custom index handler
    res = await client.get(CustomIndexAdmin.prefix_url)

    assert test_text in await res.text()
