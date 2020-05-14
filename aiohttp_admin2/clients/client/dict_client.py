import typing as t
from aiohttp_admin2.clients.client.abc import (
    AbstractClient,
    Instance,
    InstanceMapper,
    PaginatorCursor,
    PaginatorOffset,
)
from aiohttp_admin2.clients.exceptions import InstanceDoesNotExist
from aiohttp_admin2.clients.types import PK


__all__ = ['DictClient', ]


class DictClient(AbstractClient):
    """
    Dict client use dictionary as a storage. This class mainly use for test
    correct work of client abstraction.

    Usage:

        >>> storage = {1: {"name": "Bob"}, 2: {"name": "Oliver"}}
        >>> my_dict_client = DictClient(storage)
        >>> user = my_dict_client.get_one(1)

    """
    _pk: int
    engine: t.Dict[PK, t.Any]

    def __init__(self, engine: t.Optional[t.Dict[PK, t.Any]] = None):
        self.engine = engine or {}
        self._pk = self._pk or 1

    async def get_one(self, pk: PK) -> Instance:
        instance = self.engine.get(pk)

        if not instance:
            raise InstanceDoesNotExist

        return instance

    async def get_many(self, pks: t.List[PK]) -> InstanceMapper:
        return {
            pk: self.engine.get(pk)
            for pk in pks
        }

    async def get_list(
        self,
        limit=50,
        offset=None,
        cursor=None,
    ) -> t.Union[PaginatorCursor, PaginatorOffset]:
        result = []

        for pk, value in self.engine.items():
            instance = Instance()
            instance.__dict__ = {'pk': pk, **value}
            result.append(instance)

        # return Paginator(result[:limit])

    async def delete(self, pk: PK) -> None:
        if pk not in self.engine:
            raise InstanceDoesNotExist

        del self.engine[pk]

    async def create(self, instance: Instance) -> Instance:
        pk = self._get_pk()
        instance.pk = pk
        self.engine[pk] = {"pk": pk, **instance.__dict__}

        return instance

    async def update(self, pk: PK, instance: Instance) -> Instance:
        if pk not in self.engine:
            raise InstanceDoesNotExist

        self.engine[pk] = instance.__dict__

        return instance

    def _get_pk(self) -> PK:
        """Return a unique pk for new instance."""
        pk = self._pk

        while pk in self.engine:
            pk += 1

        self._pk = pk

        return pk