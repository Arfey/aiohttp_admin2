from aiohttp import web
import aiohttp_jinja2

from aiohttp_admin2.view.aiohttp.views.tab_base_view import TabBaseView

__all__ = ['TabTemplateView', ]


class TabTemplateView(TabBaseView):
    template_name: str = 'aiohttp_admin/layouts/custom_tab_page.html'

    async def get_content(self, req):
        return ''

    def get_pk(self, req):
        return req.match_info['pk']

    async def get(self, req: web.Request) -> web.Response:
        return aiohttp_jinja2.render_template(
            self.template_name,
            req,
            {
                **await self.get_context(req),
                'title': f"{self.parent.name}#{self.get_pk(req)}",
                'content': await self.get_content(req)
            },
        )

    def setup(self, app: web.Application) -> None:
        app.add_routes([
            web.get(self.index_url, self.get, name=self.index_url_name)
        ])
