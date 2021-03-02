from aiohttp_admin2.controllers.relations import ToManyRelation
from aiohttp_admin2.view import ControllerView

from .controllers import (
    MoviesController,
    ActorMovieController,
    GenreMovieController,
)
from ..images.controller import ImageController


class MoviesPage(ControllerView):
    controller = MoviesController

    relations = [
        ToManyRelation(
            name='Actors',
            left_table_pk='movie_id',
            right_table_pk='actor_id',
            relation_controller=ActorMovieController
        ),
        ToManyRelation(
            name='Genres',
            left_table_pk='movie_id',
            right_table_pk='genre_id',
            relation_controller=GenreMovieController
        ),
        ToManyRelation(
            name='Images',
            left_table_pk='movie_id',
            right_table_pk='id',
            relation_controller=ImageController
        ),
    ]
