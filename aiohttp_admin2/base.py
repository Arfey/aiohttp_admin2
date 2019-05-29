import pathlib
from typing import (
    Dict,
    Any,
)

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_jinja2 import APP_KEY
from jinja2 import ChoiceLoader

__all__ = ['Admin', ]

parent = pathlib.Path(__file__).resolve().parent
templates_dir = parent / 'templates'
static_dir = parent / 'static'


@aiohttp_jinja2.template(template_name='admin/index.html')
async def index1_handler(req: web.Request) -> Dict[str, Any]:
    return {}


class Admin:
    """
    docs
    """
    index_handler = None
    name = None
    prefix_url = '/admin/'

    def __init__(self, app: web.Application) -> None:
        self.setup_admin_application(app)

    @staticmethod
    @aiohttp_jinja2.template(template_name='admin/index.html')
    async def index_handler(req: web.Request) -> Dict[str, Any]:
        return {}

    def setup_admin_application(
        self,
        app: web.Application,
        jinja_app_key: str = APP_KEY,
    ) -> None:
        """
        docs

        :param app:
        :return:
        """
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

        aiohttp_jinja2.setup(admin, loader=admin_loader)
