import typing as t

from aiohttp_admin2.clients.abc import ABCFilter


MongoQuery = t.Dict[str, t.Any]


class MongoBaseFilter(ABCFilter):
    def __init__(
        self,
        *,
        column: str,
        value: t.Any,
        query: MongoQuery,
    ) -> None:
        self.value = value
        self.column = column
        self._query = query

    def _update_query(self, value: MongoQuery) -> MongoQuery:
        if self.column in self._query:
            self._query[self.column].update(value)

        else:
            self._query.update({self.column: value})

        return self._query


class GT(MongoBaseFilter):
    """Greater filter."""

    def apply(self) -> MongoQuery:
        return self._update_query({"$gt": self.value})


class GTE(MongoBaseFilter):
    """Greater or equal filter."""

    def apply(self) -> MongoQuery:
        return self._update_query({"$gte": self.value})


class LT(MongoBaseFilter):
    """Less filter."""

    def apply(self) -> MongoQuery:
        return self._update_query({"$lt": self.value})


class LTE(MongoBaseFilter):
    """Less or equal filter."""

    def apply(self) -> MongoQuery:
        return self._update_query({"$lte": self.value})


class EQ(MongoBaseFilter):
    """Equal filter."""

    def apply(self) -> MongoQuery:
        return self._update_query({"$eq": self.value})


class NE(MongoBaseFilter):
    """No equal filter."""

    def apply(self) -> MongoQuery:
        return self._update_query({"$ne": self.value})


class IN(MongoBaseFilter):
    """In array filter."""

    def apply(self) -> MongoQuery:
        return self._update_query({"$in": self.value})


class NIN(MongoBaseFilter):
    """Not in array filter."""

    def apply(self) -> MongoQuery:
        return self._update_query({"$nin": self.value})


class Like(MongoBaseFilter):
    """Like filter."""

    def apply(self) -> MongoQuery:
        return self._update_query({"$regex": f"/.*{self.value}.*/"})


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