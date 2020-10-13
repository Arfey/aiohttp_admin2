from aiohttp_admin2.view import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
from aiohttp_admin2.mappers import fields

from ...catalog.tables import actors
from ..injectors import postgres_injector


# todo: remove table from controller?

class ActorMapper(PostgresMapperGeneric, table=actors):
    GENDER_CHOICES = (
        ('male', "male"),
        ('female', "female"),
    )

    gender = fields.ChoicesField(
        field_cls=fields.StringField,
        choices=GENDER_CHOICES,
        default='male'
    )


@postgres_injector.inject
class ActorController(PostgresController):
    table = actors
    mapper = ActorMapper
    name = 'actor'
    per_page = 10

    list_filter = ['gender', ]
    search_fields = ['name', 'gender']


class ActorPage(ControllerView):
    controller = ActorController
