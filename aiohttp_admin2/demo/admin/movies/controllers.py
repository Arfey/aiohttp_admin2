from aiohttp_admin2.view import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric

from ...catalog.tables import movies


# todo: remove table from controller?

class MoviesMapper(PostgresMapperGeneric, table=movies):
    pass


class MoviesController(PostgresController):
    table = movies
    mapper = MoviesMapper
    engine_name = 'db'
    name = 'movies'
    per_page = 10


class MoviesPage(ControllerView):
    controller = MoviesController
