from aiohttp_admin2.view import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric

from ...catalog.tables import shows
from ...injectors import postgres_injector


# todo: remove table from controller?

class ShowsMapper(PostgresMapperGeneric, table=shows):
    pass


@postgres_injector.inject
class ShowsController(PostgresController):
    table = shows
    mapper = ShowsMapper
    name = 'shows'
    per_page = 10


class ShowsPage(ControllerView):
    controller = ShowsController
