from aiohttp import web
import aiohttp_jinja2

from aiohttp_admin2.view.aiohttp.views.base import BaseAdminView
from aiohttp_admin2.controllers.controller import Controller


class ControllerView(BaseAdminView):
    """
    This class need for represent a pages based on controller for admin
    interface.
    """
    template_list_name = 'aiohttp_admin/list.html'
    controller: Controller

    def __init__(self) -> None:
        default = self.controller.resource.name.lower()
        self.index_url = self.index_url or f'/{default}/'
        self.name = self.name or default

        self.title = self.title if not self.title == 'None' else default

    async def get_list(self, req: web.Request) -> web.Response:
        return aiohttp_jinja2.render_template(
            self.template_list_name,
            req,
            await self.get_context(req),
        )

    def setup(self, app: web.Application) -> None:
        app.add_routes([
            web.get(self.index_url, self.get_list, name=self.name)
        ])
