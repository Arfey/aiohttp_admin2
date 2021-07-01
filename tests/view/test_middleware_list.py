from aiohttp import web
from aiohttp_admin2 import setup_admin
from aiohttp_admin2.views import Admin


async def test_middleware_list(aiohttp_client):
    """
    In this test we check success apply of middleware for admin interface.

        1. Correct access for not admin page
        2. Wrong access for admin page
        3. Correct access for admin page
    """

    @web.middleware
    async def access(request, handler):
        raise web.HTTPForbidden()

    async def index(request):
        return web.Response(text="Index")

    app = web.Application()
    app.add_routes([web.get('/', index)])
    setup_admin(app, middleware_list=[access, ])

    cli = await aiohttp_client(app)

    # 1. Correct access for not admin page
    res = await cli.get('/')

    assert res.status == 200

    # 2. Wrong access for admin page
    res = await cli.get(Admin.admin_url)

    assert res.status == 403

    # 3. Correct access for admin page

    @web.middleware
    async def access(request, handler):
        # to do nothing
        return await handler(request)

    app = web.Application()
    app.add_routes([web.get('/', index)])
    setup_admin(app, middleware_list=[access, ])

    cli = await aiohttp_client(app)

    res = await cli.get(Admin.admin_url)
    assert res.status == 200
