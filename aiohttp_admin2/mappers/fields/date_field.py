from datetime import datetime, date

from aiohttp_admin2.mappers.exceptions import ValidationError
from aiohttp_admin2.mappers.fields.abc import AbstractField
from dateutil import parser

__all__ = [
    "DateTimeField",
    "DateField",
]


class DateTimeField(AbstractField):
    """
    A field for represent an standard datetime type:

    >>> from aiohttp_admin2.mappers import fields
    >>>
    >>> class Mapper(Mapper):
    >>>     field = fields.DateTimeField()
    """
    type_name: str = 'datetime'

    def to_python(self) -> datetime:
        try:
            if isinstance(self._value, datetime):
                return self._value
            return parser.parse(self._value) if self._value else None
        except parser.ParserError:
            raise ValidationError(
                f"Incorrect format for time field. {self._value}"
            )


class DateField(AbstractField):
    """
    A field for represent an standard date type:

    >>> from aiohttp_admin2.mappers import fields
    >>>
    >>> class Mapper(Mapper):
    >>>     field = fields.DateField()
    """
    type_name: str = 'date'

    def to_python(self) -> date:
        try:
            if isinstance(self._value, date):
                return self._value
            return parser.parse(self._value).date() if self._value else None
        except parser.ParserError:
            raise ValidationError(
                f"Incorrect format for time field. {self._value}"
            )
