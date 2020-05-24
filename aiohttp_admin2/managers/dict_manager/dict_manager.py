import typing as t

from aiohttp_admin2.managers.abc import (
    AbstractManager,
    Instance,
    InstanceMapper,
    Paginator,
)
from aiohttp_admin2.managers.exceptions import InstanceDoesNotExist
from aiohttp_admin2.managers.types import PK


__all__ = ['DictManager', ]


# TODO: paginator

class DictManager(AbstractManager):
    """
    Dict client use dictionary as a storage. This class mainly use for test
    correct work of client abstraction.

    Usage:

        >>> storage = {1: {"name": "Bob"}, 2: {"name": "Oliver"}}
        >>> my_dict_client = DictManager(storage)
        >>> user = my_dict_client.get_one(1)

    """
    _pk: int
    engine: t.Dict[PK, t.Any]

    def __init__(self, engine: t.Optional[t.Dict[PK, t.Any]] = None):
        self.engine = engine or {}
        self._pk = 1

    async def get_one(self, pk: PK) -> Instance:
        instance = self.engine.get(pk)

        if not instance:
            raise InstanceDoesNotExist

        return self.row_to_instance(instance)

    async def get_many(self, pks: t.List[PK]) -> InstanceMapper:
        return {
            pk: self.row_to_instance(self.engine.get(pk))
            for pk in pks
            if pk in self.engine
        }

    async def get_list(
        self,
        limit=50,
        offset=None,
        cursor=None,
        order_by=None
    ) -> Paginator:
        result = []

        for pk, value in self.engine.items():
            instance = Instance()
            instance.__dict__ = {'id': pk, **value}
            result.append(instance)

        # return result

    async def delete(self, pk: PK) -> None:
        if pk not in self.engine:
            raise InstanceDoesNotExist

        del self.engine[pk]

    async def create(self, instance: Instance) -> Instance:
        pk = self._get_pk()
        instance.id = pk
        self.engine[pk] = {"id": pk, **instance.__dict__}

        return instance

    async def update(self, pk: PK, instance: Instance) -> Instance:
        if pk not in self.engine:
            raise InstanceDoesNotExist

        self.engine[pk] = instance.__dict__

        return self.row_to_instance({
            "id": pk,
            **instance.__dict__
        })

    def _get_pk(self) -> PK:
        """Return a unique pk for new instance."""
        pk = self._pk

        while pk in self.engine:
            pk += 1

        self._pk = pk

        return pk

    def row_to_instance(self, row: t.Dict[t.Any, t.Any]) -> Instance:
        instance = Instance()
        instance.__dict__ = row

        return instance
