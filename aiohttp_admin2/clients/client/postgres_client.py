import typing as t

import sqlalchemy as sa
from aiopg.sa import Engine

from aiohttp_admin2.clients.client.abc import (
    AbstractClient,
    Instance,
    InstanceMapper,
    PaginatorOffset,
    PaginatorCursor,
)
from aiohttp_admin2.clients.exceptions import InstanceDoesNotExist
from aiohttp_admin2.clients.types import PK


__all__ = ['PostgresClient', ]


class PostgresClient(AbstractClient):
    engine: Engine
    table: sa.Table
    limit: int = 50

    def __init__(self, engine: Engine, table: sa.Table) -> None:
        self.engine = engine
        self.table = table

    async def get_one(self, pk: PK) -> Instance:
        async with self.engine.acquire() as conn:
            query = self.table\
                .select()\
                .where(self._primary_key == pk)

            cursor = await conn.execute(query)

            res = await cursor.fetchone()

            if not res:
                raise InstanceDoesNotExist

            return res

    async def get_many(self, pks: t.List[PK]) -> InstanceMapper:
        pass

    async def get_list(
        self,
        limit: int = 50,
        offset: t.Optional[int] = None,
        cursor: t.Optional[int] = None,
    ) -> t.Union[PaginatorCursor, PaginatorOffset]:
        assert offset and cursor, \
            "You can't use offset and cursor params together"

        async with self.engine.acquire() as conn:
            query = self.table\
                .select().limit(limit + 1)

            if offset is not None:
                query = query.offset(offset)
            else:
                # todo: fix problem with sorting
                query = query.where(self._primary_key >= cursor)

            cursor = await conn.execute(query)

            res = await cursor.fetchall()

            if offset is not None:
                count: int = await conn.scalar(self.table.count())
                return self.create_offset_paginator(res, limit, offset, count)
            else:
                return self.create_cursor_paginator(res, limit, cursor)


    async def delete(self, pk: PK) -> None:
        async with self.engine.acquire() as conn:
            query = self.table\
                .delete()\
                .where(self._primary_key == pk)

            await conn.execute(query)

    async def create(self, instance: Instance) -> Instance:
        data = instance.__dict__
        async with self.engine.acquire() as conn:
            query = self.table\
                .insert()\
                .values([data])\
                .returning(*self.table.c)

            cursor = await conn.execute(query)
            data = await cursor.fetchone()

            res = Instance()
            res.__dict__ = dict(data)

            return res

    async def update(self, pk: PK, instance: Instance) -> Instance:
        pass

    @property
    def _primary_key(self) -> str:
        return list(self.table.primary_key.columns)[0]
