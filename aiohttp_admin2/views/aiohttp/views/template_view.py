import aiohttp_jinja2
from aiohttp import web

from aiohttp_admin2.views.aiohttp.views.base import BaseAdminView
from aiohttp_admin2.views.aiohttp.views.utils import route


__all__ = ['TemplateView', ]


class TemplateView(BaseAdminView):
    """
    This class need for represented custom pages like dashboard or some like
    that.
    """
    template_name: str = 'aiohttp_admin/layouts/custom_page.html'

    @route('/')
    async def get(self, req: web.Request) -> web.Response:
        return aiohttp_jinja2.render_template(
            self.template_name,
            req,
            await self.get_context(req),
        )
