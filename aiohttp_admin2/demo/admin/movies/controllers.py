from aiohttp_admin2.controllers.postgres_controller import PostgresController

from .mappers import (
    ActorMoviesMapper,
    MoviesMapper,
)
from ..actors.controllers import ActorController
from ..injectors import postgres_injector
from ...catalog.tables import (
    movies,
    movies_actors,
)


__all__ = ['MoviesController', 'ActorMovieController', ]


@postgres_injector.inject
class MoviesController(PostgresController):
    table = movies
    mapper = MoviesMapper
    name = 'movies'
    per_page = 10


@postgres_injector.inject
class ActorMovieController(PostgresController):
    table = movies_actors
    mapper = ActorMoviesMapper
    inline_fields = ['id', 'movie_id', 'actor_id', 'movie']

    per_page = 10

    foreign_keys = {
        'movie_id': MoviesController,
        'actor_id': ActorController,
    }

    def movie_field(self, obj):
        return obj._relations.get('movie_id').name
