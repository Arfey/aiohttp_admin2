import typing as t

from aiohttp import web

from aiohttp_admin2.views.aiohttp.views.base import BaseAdminView

__all__ = ['TabBaseView', ]


class TabBaseView(BaseAdminView):
    _parent = None
    is_hide_view = True

    @classmethod
    def get_parent(cls):
        return cls._parent

    @classmethod
    def set_parent(cls, parent):
        cls._parent = parent

    def get_pk(self, req: web.Request) -> str:
        return req.match_info['pk']

    async def get_context(self, req: web.Request) -> t.Dict[str, t.Any]:
        return {
            ** await super().get_context(req),
            'controller_view': self,
            'pk': self.get_pk(req),
        }

    @classmethod
    def get_index_url(cls) -> str:
        return (
            f'{cls.get_parent().get_index_url()}'
            + r'{pk:\w+}' + f'/{cls.get_name()}'
        )

    @classmethod
    def get_index_url_name(cls):
        """This method return the name of the index url route."""

        name = super().get_index_url_name()

        return cls.get_parent().get_index_url_name() + "_" + name
