from typing import (
    Optional,
    Dict,
    Any,
)

from aiohttp_admin2.connectors.abc import ABCClient
from aiohttp_admin2.clients.commonts import Error
from aiohttp_admin2.clients import DOES_NOT_EXIST


__all__ = ['PostgresClient', ]

# Error(text=DOES_NOT_EXIST)


class PostgresClient(ABCClient):
    """
    docs
    """
    async def get_object_by_id(self, pk: Optional[int, str]):
        pass

    async def delete_object_by_id(self, pk: int):
        pass

    async def get_list(self, *, page: int = 1, per: int = 50):
        pass

    async def create(self, data: Dict[Any, Any]):
        pass
