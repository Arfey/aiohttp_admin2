from aiohttp_admin2.view import ControllerView

from .controllers import GenresController

__all__ = ["GenresPage", ]


class GenresPage(ControllerView):
    controller = GenresController
