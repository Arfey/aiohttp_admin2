import pathlib
import typing as t
from collections import defaultdict
from urllib.parse import urlencode

from aiohttp import web
from aiohttp_jinja2 import APP_KEY
import jinja2
import aiohttp_jinja2

from aiohttp_admin2.view import (
    DashboardView,
    BaseAdminView,
)


__all__ = ['Admin', ]


parent = pathlib.Path(__file__).resolve().parent
templates_dir = parent / 'templates'
static_dir = parent / 'static'

# todo: add test add docs
class Admin:
    """
    The main class for initialization your admin interface.
    """

    admin_name = 'aiohttp admin'
    admin_url = '/admin/'
    dashboard_class = DashboardView
    nav_groups: t.Dict[str, BaseAdminView] = None

    def __init__(
        self,
        app: web.Application,
        views: t.Optional[t.List[BaseAdminView]] = None,
    ) -> None:
        self.app = app
        self._views = [
            self.dashboard_class(),
            *[view() for view in views or []]
        ]
        self.generate_nav_groups()

    def generate_nav_groups(self):
        self.nav_groups = defaultdict(list)

        for view in self._views:
            if not view.is_hide_view:
                self.nav_groups[view.group_name].append(view)

    def init_jinja_default_env(self, env):
        env.globals.update({
            "project_name": self.admin_name,
            "nav_groups": self.nav_groups,
            "index_url": self.dashboard_class.name,
            "newParam":
                lambda new_params, params:
                    f'?{urlencode({**params, **new_params})}'
        })

    def set_views(self, app: web.Application) -> None:
        for view in self._views:
            view.setup(app)

    def setup_admin_application(
        self,
        jinja_app_key: str = APP_KEY,
    ) -> None:
        """
        This method will setup admin interface to received aiohttp application.
        """
        admin = web.Application()
        admin.router\
            .add_static('/static/', path=str(static_dir), name='admin_static')

        self.set_views(admin)
        self.app.add_subapp(self.admin_url, admin)
        self.app['aiohttp_admin'] = admin

        # setup jinja
        admin_loader = jinja2.FileSystemLoader(str(templates_dir.absolute()))

        if self.app.get(jinja_app_key):
            admin_loader = jinja2.ChoiceLoader([
                self.app.get(jinja_app_key).loader,
                admin_loader,
            ])

        env = aiohttp_jinja2.setup(admin, loader=admin_loader)

        self.init_jinja_default_env(env)
