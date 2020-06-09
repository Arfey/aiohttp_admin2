from aiohttp import web
from aiohttp_admin2 import setup_admin
from aiohttp_admin2.view.aiohttp.admin import Admin


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
