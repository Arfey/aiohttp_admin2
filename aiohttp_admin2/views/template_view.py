from aiohttp import web
import aiohttp_jinja2

from .base import BaseAdminView
from ..types import AnyDict

__all__ = ['TemplateView', ]


class TemplateView(BaseAdminView):
    """
    This class provide approach for add custom pages to the admin.
    """
    template_name: str = 'admin/simple_template.html'

    async def get_context(self, req: web.Request) -> AnyDict:
        return {
            "request": req,
            "title": self.title,
        }

    def setup(self, app: web.Application):
        @aiohttp_jinja2.template(template_name=self.template_name)
        async def handler(req: web.Request) -> AnyDict:
            return await self.get_context(req)

        app.add_routes([web.get(self.index_url, handler, name=self.name)])
