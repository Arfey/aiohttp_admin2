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


__all__ = ['MongoClient', ]


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

    async def get_list(self, count: int = 50) -> Paginator:
        pass

    async def delete(self, pk: PK) -> None:
        await self.table.collection.delete_one({"_id": ObjectId(pk)})

    async def create(self, instance: Instance) -> Instance:
        res = await self.table(**instance.__dict__).commit()

        instance.id = res.inserted_id

        return instance

    async def update(self, pk: PK, instance: Instance) -> Instance:
        pass
