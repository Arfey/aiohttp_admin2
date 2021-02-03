from aiohttp_admin2.controllers.postgres_controller import PostgresController

from ..injectors import postgres_injector
from ...catalog.tables import genres
from .mappers import GenresMapper


@postgres_injector.inject
class GenresController(PostgresController):
    table = genres
    mapper = GenresMapper
    name = 'genres'
    per_page = 10
