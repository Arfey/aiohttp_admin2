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

    inline_fields = ['id', 'name', 'type', ]
    autocomplete_search_fields = ['name', ]

    async def get_object_name(self, obj):
        return obj.data.name
