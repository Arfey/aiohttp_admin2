from typing import (
    Dict,
    Any,
)

from aiohttp import web
import aiohttp_jinja2

__all__ = ['TemplateView', ]


class TemplateView:
    """
    docs
    """
    template_name: str = None
    url: str = None
    name: str = None

    def __init__(self):
        default = self.__class__.__name__.lower()
        self.url = self.url or default
        self.name = self.name or default

    async def get_context(self):
        return {}

    def setup(self, app: web.Application):
        @aiohttp_jinja2.template(template_name=self.template_name)
        async def handler(req: web.Request) -> Dict[str, Any]:
            return await self.get_context()

        app.add_routes([web.get(self.url, handler, name=self.name)])
