import typing as t

from umongo.document import MetaDocumentImplementation
from umongo.document import DocumentImplementation
from bson.objectid import ObjectId

from aiohttp_admin2.resources.abc import AbstractResource
from aiohttp_admin2.resources.abc import Instance
from aiohttp_admin2.resources.abc import InstanceMapper
from aiohttp_admin2.resources.abc import Paginator
from aiohttp_admin2.resources.types import PK
from aiohttp_admin2.resources.mongo_resource.filters import MongoQuery
from aiohttp_admin2.resources.mongo_resource.filters import MongoBaseFilter
from aiohttp_admin2.resources.mongo_resource.filters import default_filter_mapper  # noqa
from aiohttp_admin2.resources.types import FiltersType
from aiohttp_admin2.resources.exceptions import ClientException
from aiohttp_admin2.resources.exceptions import CURSOR_PAGINATION_ERROR_MESSAGE
from aiohttp_admin2.resources.exceptions import InstanceDoesNotExist
from aiohttp_admin2.resources.exceptions import FilterException


__all__ = ['MongoResource', 'SortType', ]


SortType = t.List[t.Tuple[str, int]]


class MongoResource(AbstractResource):
    table: MetaDocumentImplementation
    filter_mapper = default_filter_mapper

    def __init__(self, table: MetaDocumentImplementation) -> None:
        self.table = table
        self.name = table.__name__.lower()

    async def get_one(self, pk: PK) -> Instance:
        data = await self.table.find_one({"_id": ObjectId(str(pk))})

        if not data:
            raise InstanceDoesNotExist

        return self._row_to_instance(data)

    async def get_many(self, pks: t.List[PK]) -> InstanceMapper:
        data = await self.table\
            .find({"_id": {"$in": [ObjectId(pk) for pk in pks]}})\
            .to_list(length=len(pks))

        relations = {
            str(r["id"]): self._row_to_instance(r)
            for r in data
        }

        return {
            _id: relations.get(_id, None)
            for _id in pks
        }

    async def get_list(
        self,
        *,
        limit=50,
        page=1,
        cursor=None,
        order_by: t.Optional[str] = None,
        filters: t.Optional[FiltersType] = None,
    ) -> Paginator:
        self._validate_list_params(page=page, cursor=cursor, limit=limit)
        sort = self.get_order(order_by)
        offset = (page - 1) * limit

        if cursor:
            if sort[0][0] not in ('id', '_id'):
                raise ClientException(CURSOR_PAGINATION_ERROR_MESSAGE)

            if int(sort[0][1]) == -1:
                query = {'_id': {'$lt': ObjectId(cursor)}}
            else:
                query = {'_id': {'$gt': ObjectId(cursor)}}

            if filters:
                query = self.apply_filters(filters=filters, query=query)

            data = await self.table\
                .find(query)\
                .limit(limit + 1)\
                .sort(sort)\
                .to_list(length=limit + 1)

        else:
            query = {}

            if filters:
                query = self.apply_filters(filters=filters, query=query)

            data = await self.table \
                .find(query)\
                .skip(offset)\
                .limit(limit + 1)\
                .sort(sort)\
                .to_list(length=limit + 1)

        data = [self._row_to_instance(i) for i in data]

        if cursor:
            return self.create_paginator(
                instances=data,
                limit=limit,
                cursor=cursor,
            )
        else:
            count: int = await self.table.count_documents(query)
            return self.create_paginator(
                instances=data,
                limit=limit,
                offset=offset,
                count=count,
            )

    async def delete(self, pk: PK) -> None:
        res = await self.table.collection.delete_one({"_id": ObjectId(pk)})

        if not res.deleted_count:
            raise InstanceDoesNotExist

    async def create(self, instance: Instance) -> Instance:
        res = await self.table(**instance.data.to_dict()).commit()

        return await self.get_one(res.inserted_id)

    async def update(self, pk: PK, instance: Instance) -> Instance:
        data = instance.data.to_dict()

        if data.get('id'):
            del data['id']

        await self.table\
            .collection\
            .update_one({"_id": ObjectId(pk)}, {"$set": data})

        return await self.get_one(pk)

    def get_order(self, order_by: str) -> SortType:
        """
        Return received order or default order if order_by was not provide.
        """
        if order_by is not None:
            if order_by.startswith("-"):
                field = order_by[1:]

                if field == 'id':
                    return [('_id', -1)]

                return [(field, -1)]

            if order_by == 'id':
                return [('_id', 1)]

            return [(order_by, 1)]

        return [('_id', -1)]

    def apply_filters(
        self,
        *,
        filters: FiltersType,
        query: MongoQuery,
    ) -> MongoQuery:
        """
        This method apply received filters.
        """
        for i in filters:
            filter_type_cls = i.filter

            if not isinstance(filters, MongoBaseFilter):
                filter_type_cls = self.filter_mapper.get(filter_type_cls)

                if not filter_type_cls:
                    raise FilterException(
                        f"unknown filter type {i.filter}")

            query = filter_type_cls(
                column=i.column_name,
                value=i.value,
                query=query,
            ).query

        return query

    def _row_to_instance(self, row: DocumentImplementation) -> Instance:
        instance = Instance()
        instance.data = row.dump()

        return instance
