from aiohttp import web
from aiohttp_admin2 import setup_admin
from aiohttp_admin2.views import (
    Admin,
    DashboardView,
)


async def test_setup_admin(aiohttp_client):
    """
    In this test we check success setup of admin interface.
    """
    app = web.Application()
    setup_admin(app)

    cli = await aiohttp_client(app)
    res = await cli.get(Admin.admin_url)

    assert res.status == 200


async def test_setup_change_index_url(aiohttp_client):
    """
    In this test we check correct work after change url to index page.
    """
    class MyAdmin(Admin):
        admin_url = '/my_url/'

    app = web.Application()
    setup_admin(app, admin_class=MyAdmin)

    cli = await aiohttp_client(app)
    res = await cli.get(MyAdmin.admin_url)

    assert res.status == 200
    assert DashboardView.title in await res.text()


async def test_setup_with_custom_dashboard(aiohttp_client):
    """
    In this test we check approach to change a start page.
    """
    class MyDashboardView(DashboardView):
        index_url = '/new'
        name = 'index_new'
        title = 'dashboard_new'

    class MyAdmin(Admin):
        dashboard_class = MyDashboardView

    app = web.Application()
    setup_admin(app, admin_class=MyAdmin)

    url = app['aiohttp_admin'].router[MyDashboardView.name].url_for()

    assert str(url) == '/admin/new'

    cli = await aiohttp_client(app)
    res = await cli.get(MyAdmin.admin_url + 'new')

    assert res.status == 200
    assert MyDashboardView.title in await res.text()
