from typing import (
    Dict,
    Any,
)

from aiohttp import web
import aiohttp_jinja2

from .base import BaseView

__all__ = ['TemplateView', ]


class TemplateView(BaseView):
    """
    docs
    """
    template_name: str = None

    async def get_context(self, req: web.Request):
        return {"request": req}

    def setup(self, app: web.Application):
        @aiohttp_jinja2.template(template_name=self.template_name)
        async def handler(req: web.Request) -> Dict[str, Any]:
            return await self.get_context(req)

        app.add_routes([web.get(self.index_url, handler, name=self.name)])
