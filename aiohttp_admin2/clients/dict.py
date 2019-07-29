from typing import (
    Optional,
    Dict,
    Any,
)

from aiohttp_admin2.connectors.abc import ABCClient
from aiohttp_admin2.clients.commonts import Error
from aiohttp_admin2.clients import DOES_NOT_EXIST


__all__ = []


class DictClient(ABCClient):
    """
    The simple implementation of ict resources for aiohttp admin. Usually,
    this resource use for test or create simple examples.
    """
    def __init__(self):
        assert self.Meta.data_list, "`data_list` is important params"

        self.mapping = {key: {key: value} for key, value in self.keys.items()}

    async def get_object_by_id(self, pk: Optional[int, str]):
        obj = self.mapping.get(pk)

        if obj:
            return obj, None

        assert None, [Error(text=DOES_NOT_EXIST)]

    async def delete_object_by_id(self, pk: int):
        try:
            obj = self.mapping.pop(pk)

            if obj:
                del self.mapping[pk]
                return obj, None
        except KeyError:
            return None, [Error(text=DOES_NOT_EXIST)]

    async def get_list(self, *, page: int = 1, per: int = 50):
        # todo: tuple with next and prev
        return self.Meta.data_list[page * per: page * per + per]

    async def create(self, data: Dict[Any, Any]):
        assert 'id' in data
        self.Meta.data_list.append(data)

        return True, None
