import typing as t
from aiohttp import web
import aiohttp_jinja2


from ..routes import routes

__all___ = ['login_page', 'login_handler', ]


@routes.get('/login')
@aiohttp_jinja2.template('login.html')
async def login_page(request: web.Request) -> t.Dict[t.Any, t.Any]:
    return {}


@routes.post('/login', name='login_post')
@aiohttp_jinja2.template('login.html')
async def login_handler(request: web.Request) -> web.Response:
    pass
