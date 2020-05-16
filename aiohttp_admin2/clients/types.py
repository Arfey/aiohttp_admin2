import typing as t

from aiohttp_admin2.clients.abc.filters import ABCFilter


__all__ = ["PK", "FilterTuple", ]


PK = t.Union[str, int]


class FilterTuple(t.NamedTuple):
    column_name: str
    value: t.Union[str, int]
    filter: t.Union[str, ABCFilter]
