import typing as t

import sqlalchemy as sa
from sqlalchemy.engine.result import RowProxy
from aiopg.sa import Engine
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy import func

from aiohttp_admin2.managers.abc import (
    AbstractManager,
    Instance,
    InstanceMapper,
    Paginator,
)
from aiohttp_admin2.managers.exceptions import (
    InstanceDoesNotExist,
    FilterException,
    CURSOR_PAGINATION_ERROR_MESSAGE,
    ClientException,
)
from aiohttp_admin2.managers.types import PK
from aiohttp_admin2.managers.postgres_manager.utils import to_column
from aiohttp_admin2.managers.types import FiltersType
from aiohttp_admin2.managers.postgres_manager.filters import (
    SQLAlchemyBaseFilter,
    default_filter_mapper,
)


__all__ = ['PostgresManager', 'SortType', ]


SortType = t.Union[sa.Column, UnaryExpression]


class PostgresManager(AbstractManager):
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

            return self.row_to_instance(res)

    async def get_many(self, pks: t.List[PK]) -> InstanceMapper:
        async with self.engine.acquire() as conn:
            query = self.table.select().where(self._primary_key.in_(pks))

            cursor = await conn.execute(query)

            return {
                r[self._primary_key.name]: self.row_to_instance(r)
                for r in await cursor.fetchall()
            }

    async def get_list(
        self,
        *,
        limit: int = 50,
        page: int = 1,
        cursor: t.Optional[int] = None,
        order_by: t.Optional[str] = None,
        filters: t.Optional[FiltersType] = None,
    ) -> Paginator:
        self._validate_list_params(page=page, cursor=cursor, limit=limit)

        offset = (page - 1) * limit

        id_orders = f"{self._primary_key.name}", f"-{self._primary_key.name}"

        if order_by not in id_orders and cursor:
            raise ClientException(CURSOR_PAGINATION_ERROR_MESSAGE)

        async with self.engine.acquire() as conn:
            query = self.table\
                .select().limit(limit + 1)

            if cursor is not None:
                if order_by == id_orders[0]:
                    query = query.where(self._primary_key > cursor)
                else:
                    query = query.where(self._primary_key < cursor)
            else:
                query = query.offset(offset)

            if filters:
                query = self.apply_filters(query=query, filters=filters)

            cursor_query = await conn\
                .execute(query.order_by(self.get_order(order_by)))

            res = [
                self.row_to_instance(r)
                for r in await cursor_query.fetchall()
            ]

            if cursor is None:
                if filters:
                    count: int = await conn.scalar(
                        self.apply_filters(
                            query=sa.select([func.count(self._primary_key)]),
                            filters=filters,
                        )
                    )
                else:
                    count: int = await conn.scalar(
                        sa.select([func.count(self._primary_key)])
                    )
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

            cursor = await conn.execute(query)
            await conn.execute('commit;')

            if not cursor.rowcount:
                raise InstanceDoesNotExist

    async def create(self, instance: Instance) -> Instance:
        data = instance.__dict__
        async with self.engine.acquire() as conn:
            query = self.table\
                .insert()\
                .values([data])\
                .returning(*self.table.c)

            cursor = await conn.execute(query)
            data = await cursor.fetchone()

            return self.row_to_instance(data)

    async def update(self, pk: PK, instance: Instance) -> Instance:
        data = instance.__dict__
        async with self.engine.acquire() as conn:
            query = self.table\
                .update()\
                .where(self._primary_key == pk)\
                .values(**data)\
                .returning(*self.table.c)

            cursor = await conn.execute(query)
            data = await cursor.fetchone()

            return self.row_to_instance(data)

    @property
    def _primary_key(self) -> sa.Column:
        """
        Return primary key for current table.
        """
        return list(self.table.primary_key.columns)[0]

    def get_order(self, order_by: str) -> SortType:
        """
        Return received order or default order if order_by was not provide.
        """
        if order_by is not None:
            if order_by.startswith("-"):
                return sa.desc(to_column(order_by[1:], self.table))
            return to_column(order_by, self.table)

        return sa.desc(self._primary_key)

    def apply_filters(
        self,
        *,
        query: sa.sql.Select,
        filters: FiltersType,
    ) -> sa.sql.Select:
        """
        This method apply received filters.
        """
        for i in filters:
            filter_type_cls = i.filter

            if not isinstance(filters, SQLAlchemyBaseFilter):
                filter_type_cls = default_filter_mapper.get(filter_type_cls)

                if not filter_type_cls:
                    raise FilterException(
                        f"unknown filter type {i.filter}")

            query = filter_type_cls(
                table=self.table,
                column=to_column(i.column_name, self.table),
                value=i.value,
                query=query,
            ).query

        return query

    def row_to_instance(self, row: RowProxy) -> Instance:
        instance = Instance()
        instance.__dict__ = dict(row)

        return instance
