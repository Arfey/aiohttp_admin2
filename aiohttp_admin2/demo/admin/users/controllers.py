from aiohttp_admin2.view import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric

from ...auth.tables import users
from ..injectors import postgres_injector


# todo: remove table from controller?

class UsersMapper(PostgresMapperGeneric, table=users):
    pass


@postgres_injector.inject
class UsersController(PostgresController):
    table = users
    mapper = UsersMapper
    name = 'users'
    per_page = 10


class UsersPage(ControllerView):
    controller = UsersController
