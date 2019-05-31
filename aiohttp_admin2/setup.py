from aiohttp import web

from .base import Admin


def setup(app: web.Application, *, admin_class: Admin = Admin) -> None:
    """
    Docs
    """
    admin_class(app).setup_admin_application()
