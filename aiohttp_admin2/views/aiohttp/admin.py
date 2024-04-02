import pathlib
import typing as t
from collections import Counter
from urllib.parse import urlencode

from aiohttp import web
from aiohttp_admin2.views.aiohttp.exceptions import NoUniqueController
from aiohttp_admin2.views.aiohttp.exceptions import NoUniqueControllerName
from aiohttp_jinja2 import APP_KEY
import jinja2
import aiohttp_jinja2

from aiohttp_admin2.views.aiohttp.utils import get_field_value
from aiohttp_admin2.views.aiohttp.views.base import global_list_view
from aiohttp_admin2.views import DashboardView
from aiohttp_admin2.views import BaseAdminView


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
    logout_path: t.Optional[str] = '/logout'

    def __init__(
        self,
        app: web.Application,
        views: t.Optional[t.List[BaseAdminView]] = None,
        middleware_list: t.Optional[t.List[t.Callable]] = None,
        logout_path: t.Optional[str] = None,
    ) -> None:
        self.app = app
        self.logout_path = logout_path
        self.middleware_list = middleware_list or []
        self._views = [
            self.dashboard_class,
            *[view for view in views or []]
        ]

    def init_jinja_default_env(self, env):
        env.globals.update({
            "project_name": self.admin_name,
            "index_url": self.dashboard_class.name,
            "logout_path": self.logout_path,
            "type_of": type,
            "get_field_value": get_field_value,
            "hasattr": hasattr,
            "getattr": getattr,
            "newParam":
                lambda new_params, params:
                    f'?{urlencode({**params, **new_params})}'
        })

    def _validate_views(self):
        """
        In this method we check all requirements for correct work of admin
        interface related with views.
        """
        if not self._views:
            return

        # The admin initialize full list of views before prepare the request.
        # It need for check access to these (for create controllers with right
        # settings). If views have the common controller than they can
        # initialize this controller in different way with different access
        # settings. In this case we don't know which settings we need to use
        # so for avoid it we need to guarantee that we use controller no more
        # than once.

        views_with_controller = [
            v for v in self._views if hasattr(v, 'controller')
        ]
        counter = Counter([v.controller for v in views_with_controller])
        most_common_controllers = counter.most_common(1)

        if most_common_controllers and most_common_controllers[0][1] > 1:
            views_with_error = [
                v for v in views_with_controller
                if v.controller == most_common_controllers[0][0]
            ]
            raise NoUniqueController(
                f"The {most_common_controllers[0][0]} controller are used more"
                f" than once for different views {views_with_error}"
            )

        # Each controller have to the unique name
        name_counter = Counter(
            [v.controller.name for v in views_with_controller]
        )
        most_common_ctr_names = name_counter.most_common(1)

        if most_common_ctr_names and most_common_ctr_names[0][1] > 1:
            controllers_with_error = [
                v.controller for v in views_with_controller
                if v.controller.name == most_common_ctr_names[0][0]
            ]
            raise NoUniqueControllerName(
                f"You already specify controllers {controllers_with_error} "
                f"with name {most_common_ctr_names[0][0]}. The controller "
                f"name must be unique.")

    def _set_views(self, app: web.Application) -> None:
        self._validate_views()
        tabs = []

        for view in self._views:
            view.setup(app)

            for tab_view in view.get_tabs():
                tabs.append(tab_view)

        global_list_view.set([*self._views, *tabs])

    def setup_admin_application(
        self,
        jinja_app_key: str = APP_KEY,
    ) -> None:
        """
        This method will setup admin interface to received aiohttp application.
        """
        admin = web.Application(middlewares=self.middleware_list)
        admin.router\
            .add_static('/static/', path=str(static_dir), name='admin_static')

        self._set_views(admin)
        # global_list_view_item = global_list_view.get()

        # async def init_views(app):
        #     global_list_view.set(global_list_view_item)

        #     yield

        # self.app.cleanup_ctx.extend([
        #     init_views,
        # ])

        self.app.add_subapp(self.admin_url, admin)
        self.app['aiohttp_admin'] = admin

        # setup jinja
        admin_loader = jinja2.FileSystemLoader(str(templates_dir.absolute()))

        if self.app.get(jinja_app_key):
            admin_loader = jinja2.ChoiceLoader([
                self.app.get(jinja_app_key).loader,
                admin_loader,
            ])

        env = aiohttp_jinja2.setup(
            admin,
            loader=admin_loader,
            lstrip_blocks=True,
            trim_blocks=True,
        )

        self.init_jinja_default_env(env)
