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
from aiohttp_admin2.clients.exceptions import ClientException, CURSOR_PAGINATION_ERROR_MESSAGE


__all__ = ['MongoClient', ]


SortType = t.List[t.Tuple[str, int]]


class MongoClient(AbstractClient):
    table: MetaDocumentImplementation

    def __init__(self, table: MetaDocumentImplementation) -> None:
        self.table = table

    async def get_one(self, pk: PK) -> Instance:
        data = await self.table.find_one({"_id": ObjectId(pk)})
        res = Instance()
        res.__dict__ = {
            key: value for key, value in data.items()
        }

        return res

    async def get_many(self, pks: t.List[PK]) -> InstanceMapper:
        pass

    async def get_list(
        self,
        limit=50,
        offset=0,
        cursor=None,
        order_by: t.Optional[SortType] = None,
    ) -> Paginator:
        sort = self.get_order(order_by)
        if cursor:
            if sort[0][0] != '_id':
                raise ClientException(CURSOR_PAGINATION_ERROR_MESSAGE)

            if int(sort[0][1]) == -1:
                cursor_query = {'_id': {'$lt': ObjectId(cursor)}}
            else:
                cursor_query = {'_id': {'$gt': ObjectId(cursor)}}

            data = await self.table\
                .find(cursor_query)\
                .limit(limit + 1)\
                .sort(self.get_order(order_by))\
                .to_list(length=limit + 1)
        else:
            data = await self.table \
                .find()\
                .skip(offset)\
                .limit(limit + 1)\
                .sort(sort)\
                .to_list(length=limit + 1)

        if cursor:
            return self.create_paginator(
                instances=data,
                limit=limit,
                cursor=cursor,
            )
        else:
            count: int = await self.table.count_documents()
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

        instance.pk = res.inserted_id

        return instance

    async def update(self, pk: PK, instance: Instance) -> Instance:
        pass

    def get_order(self, order_by: t.Optional[SortType]) -> SortType:
        """
        Return received order or default order if order_by was not provide.
        """
        # todo: maybe move to string
        if order_by is not None:
            return order_by

        return [('_id', -1)]
