import typing as t

from aiohttp_admin2.resources.abc import (
    AbstractResource,
    Instance,
    InstanceMapper,
    Paginator,
)
from aiohttp_admin2.resources.exceptions import (
    ClientException,
    CURSOR_PAGINATION_ERROR_MESSAGE,
    InstanceDoesNotExist,
    BadParameters,
)
from aiohttp_admin2.resources.types import (
    PK,
    FiltersType,
)
from aiohttp_admin2.resources.dict_resource.filters import (
    DictQuery,
    DictBaseFilter,
    default_filter_mapper,
)
from aiohttp_admin2.resources.exceptions import FilterException


__all__ = ['DictResource', ]


class DictResource(AbstractResource):
    """
    Dict client use dictionary as a storage. This class mainly use for test
    correct work of client abstraction.

    Usage:

        >>> storage = {1: {"name": "Bob"}, 2: {"name": "Oliver"}}
        >>> my_dict_client = DictResource(storage)
        >>> user = my_dict_client.get_one(1)

    """
    _pk: int
    engine: t.Dict[PK, t.Any]

    def __init__(self, engine: t.Optional[t.Dict[PK, t.Any]] = None):
        self.engine = engine or {}
        self._pk = 1
        self.name = engine.__class__.__name__.lower()

    async def get_one(self, pk: PK) -> Instance:
        instance = self.engine.get(pk)

        if not instance:
            raise InstanceDoesNotExist

        return self._row_to_instance(instance)

    async def get_many(self, pks: t.List[PK]) -> InstanceMapper:
        relations = {
            pk: self._row_to_instance(self.engine.get(pk))
            for pk in pks
            if pk in self.engine
        }

        return {
            _id: relations.get(_id, None)
            for _id in pks
        }

    async def get_list(
        self,
        limit: int = 50,
        page: int = 1,
        cursor: t.Optional[int] = None,
        order_by: t.Optional[str] = None,
        filters: t.Optional[FiltersType] = None,
        with_count: bool = True,
    ) -> Paginator:
        self._validate_list_params(page=page, cursor=cursor, limit=limit)

        query = self.apply_filters(filters=filters, query=self.engine.copy())
        offset = (page - 1) * limit

        is_desc = True
        order = 'id'
        if order_by is not None:
            order = order_by
            if order_by.startswith("-"):
                order = order_by[1:]
            else:
                is_desc = False
            if self.engine:
                if order not in list(self.engine.values())[0].keys():
                    raise BadParameters(f'Field {order} does not exist.')
                if cursor and order != 'id':
                    raise ClientException(CURSOR_PAGINATION_ERROR_MESSAGE)

        if is_desc:
            objects_list = sorted(
                query.values(),
                key=lambda x: x[order],
                reverse=True,
            )
        else:
            objects_list = sorted(
                query.values(),
                key=lambda x: x[order],
            )

        if cursor is not None:
            if is_desc:
                instances = [
                    self._row_to_instance(i)
                    for i in objects_list
                    if i['id'] < cursor
                ]

                return self.create_paginator(
                    instances=instances[:limit + 1],
                    limit=limit,
                    cursor=cursor,
                )

            instances = [
                self._row_to_instance(i)
                for i in objects_list
                if i['id'] > cursor
            ]

            return self.create_paginator(
                instances=instances[:limit + 1],
                limit=limit,
                cursor=cursor,
            )

        instances = [
            self._row_to_instance(i)
            for i in objects_list
        ]

        return self.create_paginator(
            instances=instances[offset:offset + limit + 1],
            limit=limit,
            offset=offset,
            count=len(instances) if with_count else None,
        )

    async def delete(self, pk: PK) -> None:
        if pk not in self.engine:
            raise InstanceDoesNotExist

        del self.engine[pk]

    async def create(self, instance: Instance) -> Instance:
        pk = self._get_pk()
        instance.data.id = pk
        self.engine[pk] = {"id": pk, **instance.data.__dict__}

        return instance

    async def update(self, pk: PK, instance: Instance) -> Instance:
        if pk not in self.engine:
            raise InstanceDoesNotExist

        self.engine[pk] = instance.data

        return self._row_to_instance({
            "id": pk,
            **instance.data.__dict__
        })

    def _get_pk(self) -> PK:
        """Return a unique pk for new instance."""
        pk = self._pk

        while pk in self.engine:
            pk += 1

        self._pk = pk

        return pk

    def _row_to_instance(self, row: t.Dict[t.Any, t.Any]) -> Instance:
        instance = Instance()
        instance.data = row

        return instance

    def apply_filters(
        self,
        *,
        filters: FiltersType,
        query: DictQuery,
    ) -> DictQuery:
        """
        This method apply received filters.
        """
        if not filters:
            return query

        for i in filters:
            filter_type_cls = i.filter

            if not isinstance(filters, DictBaseFilter):
                filter_type_cls = default_filter_mapper.get(filter_type_cls)

                if not filter_type_cls:
                    raise FilterException(
                        f"unknown filter type {i.filter}")

            query = filter_type_cls(
                column=i.column_name,
                value=i.value,
                query=query,
            ).query

        return query
