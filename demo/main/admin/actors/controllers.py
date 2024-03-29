from markupsafe import Markup
from aiohttp_admin2.views import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
from aiohttp_admin2.controllers.relations import ToOneRelation
from aiohttp_admin2.mappers import fields

from ...catalog.tables import actors
from ...catalog.tables import actors_hash
from ..injectors import postgres_injector


class ActorMapper(PostgresMapperGeneric, table=actors):
    GENDER_CHOICES = (
        ('male', "male"),
        ('female', "female"),
    )

    gender = fields.ChoicesField(
        field_cls=fields.StringField,
        choices=GENDER_CHOICES,
        default='male',
        required=True,
    )


@postgres_injector.inject
class ActorHashController(PostgresController, table=actors_hash):
    pass


@postgres_injector.inject
class ActorController(PostgresController, table=actors):
    mapper = ActorMapper
    name = 'actor'
    per_page = 3

    # can_create = False
    # can_update = False
    # can_view = False

    relations_to_one = [
        ToOneRelation(
            name='profile_hash',
            field_name='id',
            controller=ActorHashController,
            target_field_name='actor_id'
        )
    ]

    list_filter = ['gender', ]
    search_fields = ['name', 'gender']

    inline_fields = ['photo', 'name', 'hash']

    async def photo_field(self, obj):
        return Markup(
                '<img'
                '   src="https://image.tmdb.org/t/p/w200/{path}"'
                '   width="100"'
                ' />'
            )\
            .format(path=obj.data.url)

    async def hash_field(self, obj):
        profile = await obj.get_relation('profile_hash')
        return profile.data.hash if profile else None

    async def get_object_name(self, obj):
        return f"{obj.get_pk()} - {obj.data.name}"


class ActorPage(ControllerView):
    controller = ActorController
