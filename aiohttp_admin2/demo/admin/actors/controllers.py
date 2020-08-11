from aiohttp_admin2.view import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric

from ...catalog.tables import actors


# todo: remove table from controller?

class ActorMapper(PostgresMapperGeneric, table=actors):
    pass


class ActorController(PostgresController):
    table = actors
    mapper = ActorMapper
    engine_name = 'db'
    name = 'actor'
    per_page = 10


class ActorPage(ControllerView):
    controller = ActorController
