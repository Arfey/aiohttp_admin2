import typing as t

import sqlalchemy as sa
from aiopg.sa import Engine
from sqlalchemy.sql.elements import UnaryExpression

from aiohttp_admin2.clients.client.abc import (
    AbstractClient,
    Instance,
    InstanceMapper,
    Paginator,
)
from aiohttp_admin2.clients.exceptions import InstanceDoesNotExist
from aiohttp_admin2.clients.types import PK


__all__ = ['PostgresClient', ]


SortType = t.Union[sa.Column, UnaryExpression]


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

    # todo: move to *
    async def get_list(
        self,
        limit: int = 50,
        offset: int = 0,
        cursor: t.Optional[int] = None,
        order_by: t.Optional[SortType] = None,
    ) -> Paginator:
        assert not offset and not cursor, \
            "You can't use offset and cursor params together"

        async with self.engine.acquire() as conn:
            query = self.table\
                .select().limit(limit + 1)

            if cursor is not None:
                # todo: fix problem with sorting
                query = query.where(self._primary_key >= cursor)
            else:
                query = query.offset(offset)

            cursor = await conn\
                .execute(query.order_by(self.get_order(order_by)))

            res = await cursor.fetchall()

            if offset is not None:
                count: int = await conn.scalar(self.table.count())
                return self.create_paginator(
                    instances=res,
                    limit=limit,
                    offset=offset,
                    count=count,
                )
            else:
                return self.create_paginator(
                    instances=res,
                    limit=limit,
                    cursor=cursor,
                )

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
    def _primary_key(self) -> sa.Column:
        """
        Return primary key for current table.
        """
        return list(self.table.primary_key.columns)[0]

    def get_order(self, order_by: t.Optional[SortType]) -> SortType:
        """
        Return received order or default order if order_by was not provide.
        """
        # todo: maybe move to string
        if order_by is not None:
            return order_by

        return sa.desc(self._primary_key)
