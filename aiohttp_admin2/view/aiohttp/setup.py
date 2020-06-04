from aiohttp import web
from aiohttp_jinja2 import APP_KEY

from aiohttp_admin2.view.aiohttp.admin import Admin


__all__ = ['setup', ]


def setup(
    app: web.Application,
    *,
    admin_class=Admin,
    jinja_app_key: str = APP_KEY
) -> None:
    """
    This is a main function for initialize an admin interface for the given
    application.
    """
    admin_class(app).setup_admin_application(jinja_app_key=jinja_app_key)
