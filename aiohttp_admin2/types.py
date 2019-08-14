from enum import Enum
from typing import (
    Dict,
    Any,
    NamedTuple,
)


AnyDict = Dict[Any, Any]


class ListResult(NamedTuple):
    list_result: list
    has_next: bool
    has_prev: bool
    active_page: int
    count_items: int
    per_page: int


class SortDirectionEnum(Enum):
    """
    This enum represent all possible direction for sorting.
    """
    ASC = "asc"
    DESC = "desc"


class ListParams(NamedTuple):
    """
    This class need to declarative allocating data which needed to
    fetching list of instances.
    """
    page: int
    sort: str
    per_page: int
    sort_direction: SortDirectionEnum
