from aiohttp_admin2.views import ControllerView

from .controllers import MoviesController


class MoviesPage(ControllerView):
    controller = MoviesController
