from aiohttp_admin2.view import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric

from ...catalog.tables import genres


# todo: remove table from controller?

class GenresMapper(PostgresMapperGeneric, table=genres):
    pass


class GenresController(PostgresController):
    table = genres
    mapper = GenresMapper
    engine_name = 'db'
    name = 'genres'
    per_page = 10


class GenresPage(ControllerView):
    controller = GenresController
