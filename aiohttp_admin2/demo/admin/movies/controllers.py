from aiohttp_admin2.view import (
    ControllerView,
    ManyToManyTabView,
)
from aiohttp_admin2.controllers.postgres_controller import (
    PostgresController,
    ManyToManyPostgresController,
)
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric

from ...catalog.tables import (
    movies,
    movies_actors,
    actors,
)
from ..injectors import postgres_injector


class MoviesMapper(PostgresMapperGeneric, table=movies):
    pass


@postgres_injector.inject
class MoviesController(PostgresController):
    table = movies
    mapper = MoviesMapper
    name = 'movies'
    per_page = 10


@postgres_injector.inject
class ActorMovieController(ManyToManyPostgresController):
    table = movies_actors
    target_table = actors

    # left_table_name = movies_actors.c.actor_id
    # right_table_name = movies_actors.c.movie_id

    left_table_name = 'movie_id'
    right_table_name = 'actor_id'


class ActorTab(ManyToManyTabView):
    name = 'Actors'
    controller = ActorMovieController


class MoviesPage(ControllerView):
    controller = MoviesController
    tabs = [ActorTab, ]

