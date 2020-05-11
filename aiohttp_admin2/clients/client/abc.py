import typing as t
from abc import (
    ABC,
    abstractmethod,
)

from aiohttp_admin2.clients.types import PK


__all__ = ['AbstractClient', 'Instance', 'InstanceMapper', 'Paginator', ]


class Instance:
    """Object from represent all data connected with instance."""
    pk: PK


class Paginator(t.NamedTuple):
    """Object for represent list of instances."""
    instances: t.List[Instance]


InstanceMapper = t.Dict[PK, t.Optional[Instance]]


# todo: maybe Manager???
class AbstractClient(ABC):
    """
    All clients must be implement all method from current abstract class. These
    methods provide all action which need to do with store for work with data.
    """
    PER_PAGE = 50
    engine: t.Any = None

    @abstractmethod
    async def get_one(self, pk: PK) -> Instance:
        """
        Get one an instance from a storage. This method mainly will use for
        detail page of instance.

        Raises:
            InstanceDoesNotExist: If instance does not exists
        """

    @abstractmethod
    async def get_many(self, pks: t.List[PK]) -> InstanceMapper:
        """
        Get many instances by ids from a storage. This method will use as a
        dataloader. TThis method mainly will use on list page in cases when
        need to show field with data from related model for prevent N + 1
        problem.

        Returns:
            dict: mapping where key is a primary key and value an optional
            Instance.
        """

    @abstractmethod
    async def get_list(self, count: int = PER_PAGE) -> Paginator:
        """
        Get list of instances. This method will use for show list of instances
        and must have some features:

            - pagination
            - filtering
            - sorting
        """

    @abstractmethod
    async def delete(self, pk: PK) -> None:
        """
        Delete instance.

        Raises:
            InstanceDoesNotExist: If instance does not exists
        """

    @abstractmethod
    async def create(self, instance: Instance) -> Instance:
        """Create instance."""

    @abstractmethod
    async def update(self, pk: PK, instance: Instance) -> Instance:
        """
        Update instance.

        Raises:
            InstanceDoesNotExist: If instance does not exists
        """
