from aiohttp_admin2.view import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
from aiohttp_admin2.mappers import fields

from ...catalog.tables import genres
from .validators import validate_short_name
from ..injectors import postgres_injector


# todo: remove table from controller?

class GenresMapper(PostgresMapperGeneric, table=genres):
    name = fields.StringField(required=True, validators=[validate_short_name])


@postgres_injector.inject
class GenresController(PostgresController):
    table = genres
    mapper = GenresMapper
    name = 'genres'
    per_page = 10


class GenresPage(ControllerView):
    controller = GenresController
