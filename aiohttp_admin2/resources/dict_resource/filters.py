import typing as t

from aiohttp_admin2.resources.abc import ABCFilter


__all__ = [
    "GT",
    "GTE",
    "LT",
    "LTE",
    "EQ",
    "NE",
    "IN",
    "NIN",
    "Like",
    "DictBaseFilter",
    "DictQuery",
    "default_filter_mapper"
]


DictQuery = t.Dict[int, t.Any]


class DictBaseFilter(ABCFilter):
    def __init__(
        self,
        *,
        column: str,
        value: t.Any,
        query: DictQuery,
    ) -> None:
        self.value = value
        self.column = column
        self._query = query

    def _update_query(self, predict):
        return {
            key: value
            for key, value in self._query.items()
            if predict(value[self.column], self.value)
        }


class GT(DictBaseFilter):
    """Greater filter."""

    def apply(self) -> DictQuery:
        return self._update_query(lambda a, b: a > b)


class GTE(DictBaseFilter):
    """Greater or equal filter."""

    def apply(self) -> DictQuery:
        return self._update_query(lambda a, b: a >= b)


class LT(DictBaseFilter):
    """Less filter."""

    def apply(self) -> DictQuery:
        return self._update_query(lambda a, b: a < b)


class LTE(DictBaseFilter):
    """Less or equal filter."""

    def apply(self) -> DictQuery:
        return self._update_query(lambda a, b: a <= b)


class EQ(DictBaseFilter):
    """Equal filter."""

    def apply(self) -> DictQuery:
        return self._update_query(lambda a, b: a == b)


class NE(DictBaseFilter):
    """No equal filter."""

    def apply(self) -> DictQuery:
        return self._update_query(lambda a, b: a != b)


class IN(DictBaseFilter):
    """In array filter."""

    def apply(self) -> DictQuery:
        return self._update_query(lambda a, b: a in b)


class NIN(DictBaseFilter):
    """Not in array filter."""

    def apply(self) -> DictQuery:
        return self._update_query(lambda a, b: a not in b)


class Like(DictBaseFilter):
    """Like filter."""

    def apply(self) -> DictQuery:
        return self._update_query(lambda a, b: b in a)


default_filter_mapper = {
    'eq': EQ,
    'ne': NE,
    'lt': LT,
    'lte': LTE,
    'gt': GT,
    'gte': GTE,
    'in': IN,
    'nin': NIN,
    'like': Like,
}
