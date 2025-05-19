import typing as t
from abc import (
    ABC,
    abstractmethod,
)

from aiohttp_admin2.resources.exceptions import (
    FilterException,
    BadParameters,
)
from aiohttp_admin2.exceptions import AdminException


__all__ = [
    'AbstractResource',
    'Instance',
    'InstanceMapper',
    'Paginator',
    'ABCFilter',
    'PK',
    'FilterTuple',
    'FiltersType',
    'FilterMultiTuple',
]


PK = t.Union[str, int]


# todo: docs
class ABCFilter(ABC):
    field_name: str
    value: t.Any
    name: str

    @abstractmethod
    def apply(self) -> t.Any:
        pass

    def validate(self):
        pass

    @property
    def query(self) -> t.Any:
        try:
            self.validate()
        except Exception as e:
            msg = ""

            if e.args and isinstance(e.args[0], str):
                msg = e.args[0]

            raise FilterException(msg)

        return self.apply()


class FilterTuple(t.NamedTuple):
    column_name: str
    value: t.Union[str, t.Any]
    filter: t.Union[str, ABCFilter]


class FilterMultiTuple(t.NamedTuple):
    columns_name: t.List[str]
    value: t.Union[str, t.Any]
    filter: t.Union[str, ABCFilter]


FiltersType = t.List[FilterTuple]


class Data:

    def to_dict(self):
        return self.__dict__


class Instance:
    """Object from represent all data connected with instance."""
    pk: PK
    _name: str = None
    _prefetch_together: t.List["Instance"] = []
    _data = None

    def __init__(self, name: str = None) -> None:
        self._name = name

    @property
    def data(self) -> t.Optional[object]:
        return self._data

    @data.setter
    def data(self, data: t.Dict[str, t.Any]) -> None:
        obj = Data()
        obj.__dict__ = data
        self._data = obj

    def __repr__(self) -> str:
        return self._name or str(self.data)

    def set_name(self, name: str) -> None:
        self._name = name

    def get_pk(self) -> PK:
        if hasattr(self.data, 'pk'):
            return self.data.pk

        if hasattr(self.data, 'id'):
            return self.data.id

        raise AdminException("Instance must have id")

    @property
    def prefetch_together(self) -> t.List["Instance"]:
        if self._prefetch_together:
            return self._prefetch_together

        return [self]

    def get_relation(self, name: str) -> t.Optional["Instance"]:
        return None


class Paginator(t.NamedTuple):
    """Object for represent list of instances."""
    instances: t.List[Instance]
    has_next: bool
    has_prev: bool
    next_id: t.Optional[int]
    count: t.Optional[int]
    active_page: t.Optional[int]
    per_page: int


InstanceMapper = t.Dict[PK, t.Optional[Instance]]


class AbstractResource(ABC):
    """
    All resources must be implement all method from current abstract class.
    These methods provide all action which need to do with store for work with
    data.
    """
    engine: t.Any = None
    name: str

    @abstractmethod
    async def get_one(self, pk: PK) -> Instance:
        """
        Get one an instance from a storage. This method mainly will use for
        detail page of instance.

        Raises:
            InstanceDoesNotExist: If instance does not exists
        """

    @abstractmethod
    async def get_many(
        self,
        pks: t.List[PK],
        field: str = None,
    ) -> InstanceMapper:
        """
        Get many instances by ids from a storage. This method will use as a
        dataloader. This method mainly will use on list page in cases when
        need to show field with data from related model for prevent N + 1
        problem.

        Returns:
            dict: mapping where key is a primary key and value an optional
            Instance.
        """

    @abstractmethod
    async def get_list(
        self,
        *,
        limit: int,
        page: int = 1,
        cursor: t.Optional[int] = None,
        order_by: t.Optional[str] = None,
        filters: t.Optional[FiltersType] = None,
        with_count: bool = True,
    ) -> Paginator:
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

    def create_paginator(
        self,
        *,
        instances: t.List[Instance],
        limit: int,
        offset: t.Optional[int] = None,
        cursor: t.Optional[int] = None,
        count: t.Optional[int] = None,
    ) -> Paginator:
        has_next = len(instances) > limit
        next_id = None

        if has_next:
            last_instance = instances[-1]
            next_id = last_instance.get_pk()

        return Paginator(
            instances=instances[0:limit],
            has_next=has_next,
            has_prev=bool(offset) or bool(cursor),
            active_page=int(offset/limit + 1) if offset is not None else None,
            per_page=limit,
            count=count,
            next_id=next_id,
        )

    def _validate_list_params(
        self, *,
        page: t.Optional[int] = None,
        cursor: t.Optional[str] = None,
        limit: t.Optional[int] = None,
    ):
        if page <= 0:
            raise BadParameters("Page must be greater than zero")

        if limit <= 0:
            raise BadParameters("Limit must be greater than zero")

        if page != 1 and cursor is not None:
            raise BadParameters(
                "You can't use offset and cursor params together"
            )
