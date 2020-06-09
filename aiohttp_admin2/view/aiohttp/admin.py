import pathlib

from aiohttp import web
from aiohttp_jinja2 import APP_KEY
import jinja2
import aiohttp_jinja2


__all__ = ['Admin', ]


parent = pathlib.Path(__file__).resolve().parent
templates_dir = parent / 'templates'
static_dir = parent / 'static'


class Admin:
    """
    The main class for initialization your admin interface.
    """

    admin_name = 'aiohttp admin'
    admin_url = '/admin/'

    def __init__(self, app: web.Application) -> None:
        self.app = app

    def init_jinja_default_env(self, env):
        env.globals.update({
            "project_name": self.admin_name,
        })

    @staticmethod
    def _get_index(request: web.Request) -> web.Response:
        return aiohttp_jinja2.render_template(
            'admin/index.html',
            request,
            {},
        )

    def set_views(self, app: web.Application) -> None:
        app.add_routes([
            web.get(
                '/',
                self._get_index,
                name='index',
            )
        ])

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

        # setup jinja
        admin_loader = jinja2.FileSystemLoader(str(templates_dir.absolute()))

        if self.app.get(jinja_app_key):
            admin_loader = jinja2.ChoiceLoader([
                self.app.get(jinja_app_key).loader,
                admin_loader,
            ])

        env = aiohttp_jinja2.setup(admin, loader=admin_loader)

        self.init_jinja_default_env(env)
