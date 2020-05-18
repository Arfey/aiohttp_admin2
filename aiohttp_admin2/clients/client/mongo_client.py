import typing as t

from umongo.document import MetaDocumentImplementation
from bson.objectid import ObjectId

from aiohttp_admin2.clients.client.abc import (
    AbstractClient,
    Instance,
    InstanceMapper,
    Paginator,
)
from aiohttp_admin2.clients.types import PK
from aiohttp_admin2.clients.mongo_client.filters import (
    MongoQuery,
    MongoBaseFilter,
    default_filter_mapper,
)
from aiohttp_admin2.clients.types import FilterTuple
from aiohttp_admin2.clients.exceptions import (
    ClientException,
    CURSOR_PAGINATION_ERROR_MESSAGE,
)
from aiohttp_admin2.clients.exceptions import FilterException


__all__ = ['MongoClient', ]


SortType = t.List[t.Tuple[str, int]]
# todo: common type
FiltersType = t.List[FilterTuple]


class MongoClient(AbstractClient):
    table: MetaDocumentImplementation

    def __init__(self, table: MetaDocumentImplementation) -> None:
        self.table = table

    async def get_one(self, pk: PK) -> Instance:
        data = await self.table.find_one({"_id": ObjectId(pk)})
        res = Instance()
        res.__dict__ = data.dump()

        return res

    async def get_many(self, pks: t.List[PK]) -> InstanceMapper:
        pass

    async def get_list(
        self,
        limit=50,
        offset=0,
        cursor=None,
        order_by: t.Optional[SortType] = None,
        filters: t.Optional[FiltersType] = None,
    ) -> Paginator:
        sort = self.get_order(order_by)
        if cursor:
            if sort[0][0] != '_id':
                raise ClientException(CURSOR_PAGINATION_ERROR_MESSAGE)

            if int(sort[0][1]) == -1:
                query = {'_id': {'$lt': ObjectId(cursor)}}
            else:
                query = {'_id': {'$gt': ObjectId(cursor)}}

            if filters:
                query = self.apply_filters(filters, query)

            data = await self.table\
                .find(query)\
                .limit(limit + 1)\
                .sort(self.get_order(order_by))\
                .to_list(length=limit + 1)

        else:
            query = {}

            if filters:
                query = self.apply_filters(filters, query)

            data = await self.table \
                .find(query)\
                .skip(offset)\
                .limit(limit + 1)\
                .sort(sort)\
                .to_list(length=limit + 1)

        data = [i.dump() for i in data]

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
        await self.table.collection.delete_one({"_id": ObjectId(pk)})

    async def create(self, instance: Instance) -> Instance:
        res = await self.table(**instance.__dict__).commit()

        return await self.get_one(res.inserted_id)

    async def update(self, pk: PK, instance: Instance) -> Instance:
        await self.table\
            .collection\
            .update_one({"_id": ObjectId(pk)}, {"$set": instance.__dict__})

        return await self.get_one(pk)

    def get_order(self, order_by: t.Optional[SortType]) -> SortType:
        """
        Return received order or default order if order_by was not provide.
        """
        # todo: maybe move to string
        if order_by is not None:
            return order_by

        return [('_id', -1)]

    def apply_filters(
        self,
        filters: FiltersType,
        query: MongoQuery,
    ) -> MongoQuery:
        """
        This method apply received filters.
        """
        for i in filters:
            filter_type_cls = i.filter

            if not isinstance(filters, MongoBaseFilter):
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
