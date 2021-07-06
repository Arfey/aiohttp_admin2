import typing as t
import sqlalchemy as sa

import aiofiles
from aiohttp_admin2.views import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.resources.postgres_resource.postgres_resource import PostgresResource  # noqa
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
from aiohttp_admin2.views.widgets import CKEditorWidget
from aiohttp_admin2.mappers import fields

from ...auth.tables import users
from ..injectors import postgres_injector


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
class UsersController(PostgresController, table=users):
    mapper = UsersMapper
    resource = UserPostgresResource
    name = 'users'
    per_page = 10
    upload_to = './demo/main/static'
    inline_fields = ['id', 'create_at', 'is_superuser', 'array_c', 'data', ]
    list_filter = ['create_at', 'is_superuser', 'id']

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

    # todo: rename to inline_data_field
    async def data_field(self, obj) -> str:
        if obj.data.payload and isinstance(obj.data.payload, dict):
            return obj.data.data

        return ''

    def data_field_sort(self, is_reverse):
        if is_reverse:
            return sa.text("payload ->> 'data' desc")
        return sa.text("payload ->> 'data'")


class UsersPage(ControllerView):
    controller = UsersController
    fields_widgets = {
        "name": CKEditorWidget(),
    }
