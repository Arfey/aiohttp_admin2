from aiohttp_admin2.view import ControllerView

from .controllers import MoviesController


class MoviesPage(ControllerView):
    controller = MoviesController
