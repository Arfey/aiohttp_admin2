import typing as t

from aiohttp_admin2.clients.client.abc import (
    AbstractClient,
    Instance,
    InstanceMapper,
    Paginator,
)
from aiohttp_admin2.clients.types import PK


__all__ = ['PostgresClient', ]


class PostgresClient(AbstractClient):
    async def get_one(self, pk: PK) -> Instance:
        pass

    async def get_many(self, pks: t.List[PK]) -> InstanceMapper:
        pass

    async def get_list(self, count: int = 50) -> Paginator:
        pass

    async def delete(self, pk: PK) -> None:
        pass

    async def create(self, instance: Instance) -> Instance:
        pass

    async def update(self, pk: PK, instance: Instance) -> Instance:
        pass
