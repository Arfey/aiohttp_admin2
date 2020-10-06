import typing as t
import sqlalchemy as sa

import aiofiles
from aiohttp_admin2.view import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.resources.postgres_resource.postgres_resource import \
    PostgresResource
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
from aiohttp_admin2.widgets import (
    CKEditorWidget,
)
from aiohttp_admin2.mappers import fields

from ...auth.tables import users
from ..injectors import postgres_injector


# todo: remove table from controller?

class UsersMapper(PostgresMapperGeneric, table=users):
    avatar = fields.UrlImageField()


class UserPostgresResource(PostgresResource):
    def get_list_select(self) -> sa.sql.Select:
        """
        In this place you can redefine query.
        """
        return sa.select([
            *self.table.c,
            sa.type_coerce(sa.text("payload -> 'data'"), sa.Text)
                .label('data')
        ])


@postgres_injector.inject
class UsersController(PostgresController):
    table = users
    mapper = UsersMapper
    resource = UserPostgresResource
    name = 'users'
    per_page = 10
    upload_to = './aiohttp_admin2/demo/static'
    inline_fields = ['id', 'create_at', 'is_superuser', 'array_c', 'data', ]

    async def prepare_avatar_field(self, avatar: t.Any) -> str:
        if hasattr(avatar, 'file'):
            url = f'{self.upload_to}/{avatar.filename}'

            f = await aiofiles.open(url, mode='wb')
            await f.write(avatar.file.read())
            await f.close()

            return f'/static/{avatar.filename}'

        return avatar

    async def pre_update(self, data: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        data['avatar'] = await self.prepare_avatar_field(data['avatar'])
        return data

    async def pre_create(self, data: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        data['avatar'] = await self.prepare_avatar_field(data['avatar'])
        return data

    def data_field(self, obj) -> str:
        if obj.payload and isinstance(obj.payload, dict):
            return obj.payload.get('data', '')

        return ''

    def data_field_sort(self, is_reverse):
        if is_reverse:
            return sa.desc('data')
        return 'data'


class UsersPage(ControllerView):
    controller = UsersController
    fields_widgets = {
        "name": CKEditorWidget(),
    }
