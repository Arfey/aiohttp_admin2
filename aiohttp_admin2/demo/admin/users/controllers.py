import typing as t
import asyncio

import aiofiles
from aiohttp_admin2.view import ControllerView
from aiohttp_admin2.controllers.postgres_controller import PostgresController
from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
from aiohttp_admin2.widgets import (
    CKEditorWidget,
    FileWidget,
)
from aiohttp_admin2.mappers import fields

from ...auth.tables import users
from ..injectors import postgres_injector


# todo: remove table from controller?

class UsersMapper(PostgresMapperGeneric, table=users):
    avatar = fields.UrlFileField()


@postgres_injector.inject
class UsersController(PostgresController):
    table = users
    mapper = UsersMapper
    name = 'users'
    per_page = 10
    upload_to = './aiohttp_admin2/demo/static'

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


class UsersPage(ControllerView):
    controller = UsersController
    fields_widgets = {
        "name": CKEditorWidget(),
        "avatar": FileWidget(),
    }
