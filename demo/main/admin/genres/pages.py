from aiohttp_admin2.views import ControllerView

from .controllers import GenresController

__all__ = ["GenresPage", ]


class GenresPage(ControllerView):
    infinite_scroll = True
    controller = GenresController
