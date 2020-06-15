import aiohttp_jinja2
from aiohttp import web

from aiohttp_admin2.view.aiohttp.views.base import BaseAdminView


__all__ = ['TemplateView', ]

# todo: add test add docs
class TemplateView(BaseAdminView):
    """
    This class need for represented custom pages like dashboard or some like
    that.
    """
    template_name: str = 'aiohttp_admin/template_view.html'

    async def get(self, req: web.Request) -> web.Response:
        return aiohttp_jinja2.render_template(
            self.template_name,
            req,
            await self.get_context(req),
        )

    def setup(self, app: web.Application) -> None:
        app.add_routes([
            web.get(self.index_url, self.get, name=self.name)
        ])
