from datetime import datetime

from aiohttp_admin2.mappers.exceptions import ValidationError
from aiohttp_admin2.mappers.fields.abc import AbstractField
from dateutil import parser

__all__ = [
    "DateTimeField",
    "DateField",
]


class DateTimeField(AbstractField):
    type_name: str = 'datetime'

    def to_python(self) -> datetime:
        try:
            return parser.parse(self._value) if self._value else None
        except parser.ParserError:
            raise ValidationError(
                f"Incorrect format for time field. {self._value}"
            )


class DateField(DateTimeField):
    type_name: str = 'date'
