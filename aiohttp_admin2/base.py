import pathlib
from collections import defaultdict
from typing import (
    List,
)
from urllib.parse import urlencode

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_jinja2 import APP_KEY
from jinja2 import ChoiceLoader

from .views.dashboard import DashboardView
from .views.base import BaseAdminView

__all__ = ['Admin', ]

parent = pathlib.Path(__file__).resolve().parent
templates_dir = parent / 'templates'
static_dir = parent / 'static'


class Admin:
    """
    The main class for initialization your admin interface.
    """
    name = 'aiohttp admin'
    prefix_url = '/admin/'
    app: web.Application = None
    views: List[BaseAdminView] = None
    dashboard_class = DashboardView

    def __init__(self, app: web.Application) -> None:
        self.app = app
        if self.views:
            self._views = [
                view_class() for view_class in self.views 
            ]
        else:
            self._views = []

    def init_jinja_default_env(self, env):
        nav_groups = defaultdict(list)

        for view in self._views:
            if not view.is_hide_view:
                nav_groups[view.group_name].append(view)

        env.globals.update({
            "project_name": self.name,
            "nav_groups": nav_groups,
            "newParam": lambda newParam, params: f'?{urlencode({**params, **newParam})}'
        })

    def set_views(self, admin: web.Application) -> None:
        self.dashboard_class().setup(admin)

        for view in self._views:
            view.setup(admin)

        self._views.insert(0, self.dashboard_class())

    def setup_admin_application(
        self,
        jinja_app_key: str = APP_KEY,
    ) -> None:
        """
        docs

        :return:
        """
        admin = web.Application()
        self.set_views(admin)
        admin.router.add_static(
            '/static/',
            path=str(static_dir),
            name='admin_static',
        )
        self.app.add_subapp(self.prefix_url, admin)

        admin_loader = jinja2.FileSystemLoader(str(templates_dir.absolute()))

        if self.app.get(jinja_app_key):
            admin_loader = ChoiceLoader([
                self.app.get(jinja_app_key).loader,
                admin_loader,
            ])

        env = aiohttp_jinja2.setup(admin, loader=admin_loader)

        self.init_jinja_default_env(env)
