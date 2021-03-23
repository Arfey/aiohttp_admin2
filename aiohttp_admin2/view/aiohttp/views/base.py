import typing as t
from aiohttp import web

from aiohttp_admin2.view.aiohttp.utils import get_field_value
from aiohttp_admin2.view.aiohttp.views.utils import ViewUtilsMixin


__all__ = ['BaseAdminView', ]


class BaseAdminView(ViewUtilsMixin):
    """
    The base class for all admin view.
    """
    index_url: str = None
    name: str = None
    title: str = 'None'
    icon: str = 'label'
    group_name: str = 'General'
    is_hide_view: bool = False

    def __init__(self, *, params: t.Dict[str, t.Any] = None) -> None:
        default = self.__class__.__name__.lower()
        self.index_url = self.index_url or f'/{default}/'
        self.name = self.name or default
        self.title = self.title if not self.title == 'None' else default
        self.params = params or {}

    async def get_context(self, req: web.Request) -> t.Dict[str, t.Any]:
        """
        In this place you can redefine whole context which will use for
        generate custom page.
        """
        return {
            "request": req,
            "title": self.title,
            "controller_view": self,
            "type_of": type,
            "get_field_value": get_field_value,
            "url_query": req.rel_url.query,
            "url_path": req.rel_url.path,
        }

    def setup(self, app: web.Application) -> None:
        raise NotImplemented
