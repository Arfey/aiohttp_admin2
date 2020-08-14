import typing as t

from aiohttp import web
from aiohttp_jinja2 import APP_KEY

from aiohttp_admin2.view import (
    Admin,
    BaseAdminView,
)


__all__ = ['setup_admin', ]


def setup_admin(
    app: web.Application,
    *,
    engines: t.Optional[t.Dict[str, t.Any]] = None,
    admin_class=Admin,
    jinja_app_key: str = APP_KEY,
    views: t.Optional[t.List[BaseAdminView]] = None,
    middleware_list: t.Optional[t.List[t.Callable]] = None,
    logout_path: t.Optional[str] = None,
) -> None:
    """
    This is a main function for initialize an admin interface for the given
    aiohttp application.
    """
    admin_class(
        app,
        engines,
        views,
        middleware_list,
        logout_path,
    ).setup_admin_application(jinja_app_key=jinja_app_key)
