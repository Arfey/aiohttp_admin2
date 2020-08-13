from aiohttp import web
import aiohttp_jinja2
from aiohttp_security import (
    remember,
    forget,
    is_anonymous,
)

from ..routes import routes


__all___ = ['login_page', 'login_handler', ]


@routes.get('/')
async def index_page(request: web.Request) -> None:
    """
    The handler redirect user from index page to login if user is not
    authorized and to admin in other case.
    """
    if await is_anonymous(request):
        raise web.HTTPFound('/login')
    else:
        raise web.HTTPFound('/admin/')


@routes.get('/login')
@aiohttp_jinja2.template('login.html')
async def login_page(request: web.Request) -> None:
    """
    This handler represent a form for authorization user. If user is authorized
    we'll redirect him to admin page.
    """
    if not await is_anonymous(request):
        raise web.HTTPFound('/admin/')


@routes.post('/login', name='login_post')
@aiohttp_jinja2.template('login.html')
async def login_post(request: web.Request) -> None:
    """
    This handler check if user type a correct credential and do login for him
    in another case we'll redirect him to login page.
    """
    data = await request.post()

    if data['username'] == 'admin' and data['password'] == 'admin':
        admin_page = web.HTTPFound('/admin/')
        await remember(request, admin_page, 'admin')
        raise admin_page

    raise web.HTTPFound('/login')


@routes.get('/logout')
async def logout_page(request: web.Request) -> None:
    """
    This handler need for logout user and redirect him to login page.
    """
    redirect_response = web.HTTPFound('/login')
    await forget(request, redirect_response)
    raise redirect_response
