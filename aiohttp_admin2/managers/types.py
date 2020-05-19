import typing as t

from aiohttp_admin2.managers.abc import (
    ABCFilter,
    PK,
)


__all__ = ["PK", "FilterTuple", "FiltersType", ]


class FilterTuple(t.NamedTuple):
    column_name: str
    value: t.Union[str, int]
    filter: t.Union[str, ABCFilter]


FiltersType = t.List[FilterTuple]
