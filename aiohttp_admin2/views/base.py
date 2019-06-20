from aiohttp import web

__all__ = ['BaseView', ]


class BaseView:
    """
    docs
    """
    index_url: str = None
    name: str = None
    title: str = 'None'
    icon: str = 'label'
    group_name: str = 'General'
    is_hide_view: bool = False

    def __init__(self) -> None:
        default = self.__class__.__name__.lower()
        self.index_url = self.index_url or f'/{default}/'
        self.name = self.name or default

    def setup(self, app: web.Application) -> None:
        raise NotImplemented
