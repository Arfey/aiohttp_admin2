import sqlalchemy as sa
import typing as t

from aiohttp_admin2.resources.abc import ABCFilter
from aiohttp_admin2.resources.exceptions import FilterException


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
    "SQLAlchemyBaseFilter",
    "default_filter_mapper",
]


comparator_map = {
    sa.String: ('eq', 'ne', 'like', 'in', 'nin',),
    sa.Integer: ('eq', 'ne', 'lt', 'lte', 'gt', 'gte', 'in', 'nin', ),
    sa.Float: ('eq', 'ne', 'lt', 'lte', 'gt', 'gte', ),
    sa.Date: ('eq', 'ne', 'lt', 'lte', 'gt', 'gte', ),
    sa.DateTime: ('eq', 'ne', 'lt', 'lte', 'gt', 'gte', ),
    sa.Time: ('eq', 'ne', 'lt', 'lte', 'gt', 'gte', ),
    sa.Boolean: ('eq', 'ne'),
}


class SQLAlchemyBaseFilter(ABCFilter):
    filter_type: str

    def __init__(
        self,
        table: sa.Table,
        column: sa.Column,
        *,
        value: t.Any,
        query: sa.sql.Select,
    ) -> None:
        self.table = table
        self.value = value
        self.column = column
        self.columns = [column]
        self._query = query

        if not hasattr(self, 'filter_type'):
            raise FilterException(
                f"filter_type is not defined in {self.__class__}"
            )

    def _get_column_base(self, column: sa.Column) -> t.Any:
        column_type = None

        for key in comparator_map.keys():
            if isinstance(column.type, key):
                column_type = key

        return column_type

    def validate(self):
        for column in self.columns:
            base_column = comparator_map.get(self._get_column_base(column))

            if base_column and self.filter_type not in base_column:
                raise FilterException(
                    f"{self.filter_type} operation is not supported for "
                    f"{column} column."
                )


class SQLAlchemyMultiBaseFilter(SQLAlchemyBaseFilter):
    filter_type: str

    def __init__(
        self,
        table: sa.Table,
        columns: t.List[sa.Column],
        *,
        value: t.Any,
        query: sa.sql.Select,
    ) -> None:
        self.table = table
        self.value = value
        self.columns = columns
        self._query = query

        if not hasattr(self, 'filter_type'):
            raise FilterException(
                f"filter_type is not defined in {self.__class__}"
            )


class GT(SQLAlchemyBaseFilter):
    """Greater filter."""
    filter_type: str = 'gt'

    def apply(self) -> sa.sql.Select:
        return self._query.where(self.column > self.value)


class GTE(SQLAlchemyBaseFilter):
    """Greater or equal filter."""
    filter_type: str = 'gte'

    def apply(self) -> sa.sql.Select:
        return self._query.where(self.column >= self.value)


class LT(SQLAlchemyBaseFilter):
    """Less filter."""
    filter_type: str = 'lt'

    def apply(self) -> sa.sql.Select:
        return self._query.where(self.column < self.value)


class LTE(SQLAlchemyBaseFilter):
    """Less or equal filter."""
    filter_type: str = 'lte'

    def apply(self) -> sa.sql.Select:
        return self._query.where(self.column <= self.value)


class EQ(SQLAlchemyBaseFilter):
    """Equal filter."""
    filter_type: str = 'eq'

    def apply(self) -> sa.sql.Select:
        return self._query.where(self.column == self.value)


class NE(SQLAlchemyBaseFilter):
    """No equal filter."""
    filter_type: str = 'ne'

    def apply(self) -> sa.sql.Select:
        return self._query.where(self.column != self.value)


class IN(SQLAlchemyBaseFilter):
    """In array filter."""
    filter_type: str = 'in'

    def apply(self) -> sa.sql.Select:
        return self._query.where(self.column.in_(self.value))


class NIN(SQLAlchemyBaseFilter):
    """Not in array filter."""
    filter_type: str = 'nin'

    def apply(self) -> sa.sql.Select:
        return self._query.where(~self.column.in_(self.value))


class Like(SQLAlchemyBaseFilter):
    """Like filter."""
    filter_type: str = 'like'

    def apply(self) -> sa.sql.Select:
        return self._query.where(self.column.like(f'%{self.value}%'))


class SearchMulti(SQLAlchemyMultiBaseFilter):
    """Like filter with lower function for multiple fields."""
    filter_type: str = 'like'

    def make_lover(self, column):
        return sa.func.lower(column).like(f'%{str(self.value).lower()}%')

    def apply(self) -> sa.sql.Select:
        return self._query.where(
            sa.or_(*[self.make_lover(c) for c in self.columns])
        )


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
    'search_multi': SearchMulti,
}
