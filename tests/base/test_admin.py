from aiohttp import web
from aiohttp_admin2.base import Admin


def test_simple_admin():
    app = web.Application()
    Admin(app)
    assert True
