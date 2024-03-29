import typing as t

from aiohttp import web
from aiohttp_security import is_anonymous
from aiohttp_security import permits


@web.middleware
async def admin_access_middleware(
    request: web.Request,
    handler: t.Any,
) -> web.Response:
    """
    This middleware need for forbidden access to admin interface for users who
    don't have right permissions.
    """
    if await is_anonymous(request):
        raise web.HTTPFound('/')

    if not await permits(request, 'admin'):
        raise web.HTTPFound('/')

    return await handler(request)
