import pathlib
from typing import (
    Dict,
    Any,
    List,
)

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_jinja2 import APP_KEY
from jinja2 import ChoiceLoader

from .contrib.models import ModelView

__all__ = ['Admin', ]

parent = pathlib.Path(__file__).resolve().parent
templates_dir = parent / 'templates'
static_dir = parent / 'static'


class Admin:
    """
    docs
    """
    index_handler = None
    name = 'aiohttp admin'
    prefix_url = '/admin/'
    app: web.Application = None
    models: List[ModelView] = None

    def __init__(self, app: web.Application) -> None:
        self.app = app

    @staticmethod
    @aiohttp_jinja2.template(template_name='admin/index.html')
    async def index_handler(req: web.Request) -> Dict[str, Any]:
        return {}

    def init_jinja_default_env(self, env):
        env.globals.update({
            "project_name": self.name,
            "nav_items": [model.name for model in self.models],
        })

    def setup_admin_application(
        self,
        jinja_app_key: str = APP_KEY,
    ) -> None:
        """
        docs

        :return:
        """
        app = self.app
        admin = web.Application()
        admin.add_routes([web.get('/', self.index_handler, name='index')])
        admin.router.add_static(
            '/static/',
            path=str(static_dir),
            name='admin_static',
        )
        app.add_subapp(self.prefix_url, admin)

        admin_loader = jinja2.FileSystemLoader(str(templates_dir.absolute()))

        if app.get(jinja_app_key):
            admin_loader = ChoiceLoader([
                app.get(jinja_app_key).loader,
                admin_loader,
            ])

        env = aiohttp_jinja2.setup(admin, loader=admin_loader)

        self.init_jinja_default_env(env)
