import typing as t
import logging

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.engine.row import RowProxy
from sqlalchemy.sql.elements import UnaryExpression
from aiopg.sa import Engine

from aiohttp_admin2.resources.abc import AbstractResource
from aiohttp_admin2.resources.abc import Instance
from aiohttp_admin2.resources.abc import InstanceMapper
from aiohttp_admin2.resources.abc import Paginator
from aiohttp_admin2.resources.abc import FilterMultiTuple
from aiohttp_admin2.resources.exceptions import InstanceDoesNotExist
from aiohttp_admin2.resources.exceptions import FilterException
from aiohttp_admin2.resources.exceptions import CURSOR_PAGINATION_ERROR_MESSAGE
from aiohttp_admin2.resources.exceptions import ClientException
from aiohttp_admin2.resources.types import PK
from aiohttp_admin2.resources.postgres_resource.utils import to_column
from aiohttp_admin2.resources.types import FiltersType
from aiohttp_admin2.resources.postgres_resource.filters import SQLAlchemyBaseFilter  # noqa
from aiohttp_admin2.resources.postgres_resource.filters import default_filter_mapper  # noqa


__all__ = ['PostgresResource', 'SortType', ]


SortType = t.Union[sa.Column, UnaryExpression]
logger = logging.getLogger('aiohttp_admin.resource')


class PostgresResource(AbstractResource):
    engine: Engine
    table: sa.Table
    limit: int = 50
    name: str
    custom_sort_list: t.Dict[str, t.Callable] = {}
    filter_map = default_filter_mapper

    # todo: *
    def __init__(
        self,
        engine: Engine,
        table: sa.Table,
        custom_sort_list: t.Dict[str, t.Callable] = None,
    ) -> None:
        self.engine = engine
        self.table = table
        self.name = table.name.lower()
        self.custom_sort_list = custom_sort_list or {}

    async def _execute(self, conn, query):
        return await conn.execute(query)

    async def _execute_scalar(self, conn, query):
        res = await self._execute(conn, query)
        return await res.scalar()

    def get_one_select(self) -> sa.sql.Select:
        """
        In this place you can redefine query.
        """
        return self.table.select()

    async def get_one(self, pk: PK) -> Instance:
        async with self.engine.acquire() as conn:
            query = self.get_one_select()\
                .where(self._primary_key == pk)

            cursor = await self._execute(conn, query)

            res = await cursor.fetchone()

            if not res:
                raise InstanceDoesNotExist

            return self._row_to_instance(res)

    async def get_many(
        self,
        pks: t.List[PK],
        field: str = None,
    ) -> InstanceMapper:
        column = sa.column(field) if field else self._primary_key
        async with self.engine.acquire() as conn:
            query = self.table.select().where(column.in_(pks))
            cursor = await self._execute(conn, query)

            relations = {}
            relations_list = []
            multiple_instances_per_key = False

            for r in await cursor.fetchall():
                instance = self._row_to_instance(r, relations_list)

                if field:
                    pk = getattr(instance, field)
                else:
                    pk = instance.get_pk()

                relations_list.append(instance)

                if relations.get(pk):
                    multiple_instances_per_key = True

                relations[pk] = instance

            if multiple_instances_per_key:
                logger.warning(
                    "`get_many` function return multiple instances for "
                    "single pk"
                )

            return {_id: relations.get(_id, None) for _id in pks}

    def get_list_select(self) -> sa.sql.Select:
        """
        In this place you can redefine query.
        """
        return self.table.select()

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
            query = self.get_list_select()\
                .limit(limit + 1)

            if cursor is not None:
                if order_by == id_orders[0]:
                    query = query.where(self._primary_key > cursor)
                else:
                    query = query.where(self._primary_key < cursor)
            else:
                query = query.offset(offset)

            if filters:
                query = self.apply_filters(query=query, filters=filters)

            cursor_query = await self\
                ._execute(conn, query.order_by(self.get_order(order_by)))

            res = []

            for r in await cursor_query.fetchall():
                res.append(self._row_to_instance(r, res))

            if cursor is None:
                if filters:
                    count: int = await self._execute_scalar(
                        conn,
                        self.apply_filters(
                            query=(
                                sa.select(func.count(self._primary_key))
                                .select_from(self.get_list_select())
                            ),
                            filters=filters,
                        )
                    )
                else:
                    count: int = await self._execute_scalar(
                        conn,
                        sa.select(func.count()).select_from(
                            self.get_list_select()
                        )
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

            cursor = await self._execute(conn, query)
            await self._execute(conn, 'commit;')

            if not cursor.rowcount:
                raise InstanceDoesNotExist

    async def create(self, instance: Instance) -> Instance:
        data = instance.data.to_dict()
        async with self.engine.acquire() as conn:
            query = self.table\
                .insert()\
                .values([data])\
                .returning(*self.table.c)

            cursor = await self._execute(conn, query)
            data = await cursor.fetchone()

            return self._row_to_instance(data)

    async def update(self, pk: PK, instance: Instance) -> Instance:
        data = instance.data.to_dict()

        async with self.engine.acquire() as conn:
            query = self.table\
                .update()\
                .where(self._primary_key == pk)\
                .values(**data)\
                .returning(*self.table.c)

            cursor = await self._execute(conn, query)
            data = await cursor.fetchone()

            return self._row_to_instance(data)

    @property
    def _primary_key(self) -> sa.Column:
        """
        Return primary key for current table.
        """
        return list(self.table.primary_key.columns)[0]

    def get_order(self, order_by: str) -> SortType:
        """
        Apply received order or default order if order_by was not provide to
        query.
        """
        if order_by is not None:
            if order_by.startswith("-"):
                if self.custom_sort_list.get(order_by[1:]):
                    return self.custom_sort_list.get(order_by[1:])(True)
                return sa.desc(to_column(order_by[1:], self.table))

            if self.custom_sort_list.get(order_by):
                return self.custom_sort_list.get(order_by)(False)

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

            if (
                isinstance(filter_type_cls, str) or
                not issubclass(filter_type_cls, SQLAlchemyBaseFilter)
            ):
                filter_type_cls = self.filter_map.get(filter_type_cls)

                if not filter_type_cls:
                    raise FilterException(
                        f"unknown filter type {i.filter}")

            if isinstance(i, FilterMultiTuple):
                query = filter_type_cls(
                    self.table,
                    columns=[to_column(c, self.table) for c in i.columns_name],
                    value=i.value,
                    query=query,
                ).query
            else:

                query = filter_type_cls(
                    self.table,
                    column=to_column(i.column_name, self.table),
                    value=i.value,
                    query=query,
                ).query

        return query

    def object_name(self, row: RowProxy) -> str:
        return f'<{self.name} id={row.id}>'

    def _row_to_instance(
        self,
        row: RowProxy,
        prefetch_together: t.List[Instance] = None,
    ) -> Instance:
        instance = Instance()
        instance.data = dict(row)
        instance.set_name(self.object_name(row))

        if prefetch_together is None:
            instance._prefetch_together = [instance]

        instance._prefetch_together = prefetch_together

        return instance
