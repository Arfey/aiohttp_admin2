from aiohttp import web

from .base import Admin

__all__ = ['setup', ]


def setup(app: web.Application, *, admin_class=Admin) -> None:
    """
    Docs
    """
    admin_class(app).setup_admin_application()
