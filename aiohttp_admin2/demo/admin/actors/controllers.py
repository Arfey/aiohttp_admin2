from aiohttp_admin2.view import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
from aiohttp_admin2.controllers.relations import ToOneRelation
from aiohttp_admin2.mappers import fields

from ...catalog.tables import (
    actors,
    actors_hash,
)
from ..injectors import postgres_injector


# todo: remove table from controller?

class ActorHashMapper(PostgresMapperGeneric, table=actors_hash):
    pass


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
class ActorHashController(PostgresController):
    table = actors_hash
    mapper = ActorHashMapper


@postgres_injector.inject
class ActorController(PostgresController):
    table = actors
    mapper = ActorMapper
    name = 'actor'
    per_page = 10

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
        return f'<img ' \
               f'src="https://image.tmdb.org/t/p/w200/' \
               f'{obj.data.url}"' \
               f'width="100">'

    photo_field.is_safe = True

    async def hash_field(self, obj):
        profile = await obj.get_relation('profile_hash')
        return profile.data.hash if profile else None

    async def get_object_name(self, obj):
        return f"{obj.get_pk()} - {obj.data.name}"


class ActorPage(ControllerView):
    controller = ActorController
