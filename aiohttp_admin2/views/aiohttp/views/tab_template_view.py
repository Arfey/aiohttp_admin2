from aiohttp import web
import aiohttp_jinja2

from aiohttp_admin2.views.aiohttp.views.tab_base_view import TabBaseView
from aiohttp_admin2.views.aiohttp.views.base import BaseAdminView
from aiohttp_admin2.views.aiohttp.views.utils import route

__all__ = ['TabTemplateView', ]


class TabTemplateView(TabBaseView, BaseAdminView):
    template_name: str = 'aiohttp_admin/layouts/custom_tab_page.html'

    async def get_content(self, req: web.Request) -> str:
        return ''

    @route(r'/')
    async def get(self, req: web.Request) -> web.Response:
        return aiohttp_jinja2.render_template(
            self.template_name,
            req,
            {
                **await self.get_context(req),
                'title': f"{self.get_parent().name}#{self.get_pk(req)}",
                'content': await self.get_content(req)
            },
        )
