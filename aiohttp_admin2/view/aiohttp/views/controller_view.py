from aiohttp import web
import aiohttp_jinja2
import typing as t

from aiohttp_admin2.view.aiohttp.views.base import BaseAdminView
from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.view.aiohttp.utils import (
    get_params_from_request,
    QueryParams,
)


class ControllerView(BaseAdminView):
    """
    This class need for represent a pages based on controller for admin
    interface.
    """
    template_list_name = 'aiohttp_admin/list.html'
    controller: Controller

    def __init__(self, *, params: t.Dict[str, t.Any] = None) -> None:
        default = self.controller.name.lower()
        self.index_url = self.index_url or f'/{default}/'
        self.name = self.name or default

        self.title = self.title if not self.title == 'None' else default
        self.params = params or {}

    def get_params_from_request(self, req: web.Request) -> QueryParams:
        return get_params_from_request(req)

    def get_controller(self):
        return self.controller.builder_form_params(self.params)

    async def get_list(self, req: web.Request) -> web.Response:
        params = self.get_params_from_request(req)
        controller = self.get_controller()
        data = await controller.get_list(**params._asdict())
        return aiohttp_jinja2.render_template(
            self.template_list_name,
            req,
            {
                **await self.get_context(req),
                "list": data,
                "controller": controller,
            }
        )

    def setup(self, app: web.Application) -> None:
        app.add_routes([
            web.get(self.index_url, self.get_list, name=self.name)
        ])
