from aiohttp import web
import aiohttp_jinja2
from aiohttp_security import remember
from aiohttp_security import forget
from aiohttp_security import is_anonymous

from ..routes import routes
from .users import user_map


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
async def login_post(request: web.Request) -> web.Response:
    """
    This handler check if user type a correct credential and do login for him
    in another case we'll redirect him to login page.
    """
    data = await request.post()
    user = user_map.get(data['username'])

    if user and user.password == data['password']:
        admin_page = web.HTTPFound('/admin/')
        await remember(request, admin_page, user.username)

        # return instead raise an error to set cookies
        # https://github.com/aio-libs/aiohttp/issues/5181
        return admin_page

    raise web.HTTPFound('/login')


@routes.get('/logout')
async def logout_page(request: web.Request) -> web.Response:
    """
    This handler need for logout user and redirect him to login page.
    """
    redirect_response = web.HTTPFound('/login')
    await forget(request, redirect_response)
    # return instead raise an error to set cookies
    # https://github.com/aio-libs/aiohttp/issues/5181
    return redirect_response
