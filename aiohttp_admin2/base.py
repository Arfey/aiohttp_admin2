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

templates_dir = pathlib.Path(__file__).resolve().parent / 'templates'
new_dir = pathlib.Path(__file__).resolve().parent / 'template'


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
        app.add_subapp(self.prefix_url, admin)

        admin_loader = jinja2.FileSystemLoader(str(templates_dir.absolute()))

        if app.get(jinja_app_key):
            admin_loader = ChoiceLoader([
                app.get(jinja_app_key).loader,
                admin_loader,
            ])

        aiohttp_jinja2.setup(admin, loader=admin_loader)


if __name__ == '__main__':
    app1 = web.Application()
    loader = jinja2.FileSystemLoader(str(new_dir.absolute()))
    aiohttp_jinja2.setup(app1, loader=loader)

    Admin(app1)
    app1.add_routes([web.get('/', index1_handler, name='index')])
    web.run_app(app1)
