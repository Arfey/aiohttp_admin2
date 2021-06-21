import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import is_anonymous
from aiohttp_security import permits
from aiohttp_security import remember
from aiohttp_security import forget
from aiohttp_security import AbstractAuthorizationPolicy


class AuthorizationPolicy(AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None) -> bool:
        if identity == 'admin' and permission == 'admin':
            return True

        return False

    async def authorized_userid(self, identity) -> int:
        return identity


@web.middleware
async def admin_access_middleware(request, handler):
    if await is_anonymous(request):
        raise web.HTTPFound('/')

    if not await permits(request, 'admin'):
        raise web.HTTPFound('/')

    return await handler(request)


@aiohttp_jinja2.template('login.html')
async def login_page(request: web.Request) -> None:
    if not await is_anonymous(request):
        raise web.HTTPFound('/admin/')


@aiohttp_jinja2.template('login.html')
async def login_post(request: web.Request) -> None:
    data = await request.post()

    if data['username'] == 'admin' and 'admin' == data['password']:
        admin_page = web.HTTPFound('/admin/')
        await remember(request, admin_page, 'admin')
        raise admin_page

    raise web.HTTPFound('/login')


async def logout_page(request: web.Request) -> None:
    redirect_response = web.HTTPFound('/login')
    await forget(request, redirect_response)
    raise redirect_response
