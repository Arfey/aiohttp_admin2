from aiohttp_admin2.controllers.relations import CrossTableRelation
from aiohttp_admin2.view import ControllerView

from .controllers import (
    MoviesController,
    ActorMovieController,
)


class MoviesPage(ControllerView):
    controller = MoviesController

    relations = [
        CrossTableRelation(
            name='Actors',
            left_table_pk='movie_id',
            right_table_pk='actor_id',
            relation_controller=ActorMovieController
        ),
    ]
