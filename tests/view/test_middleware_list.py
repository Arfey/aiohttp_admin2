from aiohttp import web
from aiohttp_admin2 import setup_admin
from aiohttp_admin2.views import Admin

from .utils import generate_new_admin_class


async def index(request):
    return web.Response(text="Index")


async def test_that_middleware_work_only_for_admin_pages(aiohttp_client):
    """
    In this test we check success apply of middleware for admin interface.

        1. Correct access for not admin page
        2. Wrong access for admin page
    """

    @web.middleware
    async def access(request, handler):
        raise web.HTTPForbidden()

    app = web.Application()
    app.add_routes([web.get('/', index)])
    admin = generate_new_admin_class()
    setup_admin(app, middleware_list=[access, ], admin_class=admin)

    cli = await aiohttp_client(app)

    # 1. Correct access for not admin page
    res = await cli.get('/')

    assert res.status == 200

    # 2. Wrong access for admin page
    res = await cli.get(Admin.admin_url)

    assert res.status == 403



async def test_that_admin_pages_are_available_if_pass_middleware(aiohttp_client):
    """
    In this test we check success apply of middleware for admin interface.

        1. Correct access for admin page
    """

    @web.middleware
    async def access(request, handler):
        # to do nothing
        return await handler(request)

    app = web.Application()
    app.add_routes([web.get('/', index)])
    admin = generate_new_admin_class()
    setup_admin(app, middleware_list=[access, ], admin_class=admin)

    cli = await aiohttp_client(app)

    res = await cli.get(Admin.admin_url)
    assert res.status == 200
