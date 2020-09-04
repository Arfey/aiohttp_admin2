import typing as t
from dateutil import parser
from datetime import datetime

from aiohttp_admin2.mappers.fields.abc import AbstractField


__all__ = [
    "StringField",
    "IntField",
    "FloatField",
    "DateTimeField",
    "BooleanField",
]


class StringField(AbstractField):

    def to_python(self) -> t.Optional[str]:
        return str(self._value) if self._value else self._value


class IntField(AbstractField):

    def to_python(self) -> t.Optional[int]:
        return int(self._value) if self._value else self._value


class FloatField(AbstractField):

    def to_python(self) -> t.Optional[float]:
        return float(self._value) if self._value else self._value


class DateTimeField(AbstractField):

    def to_python(self) -> datetime:
        return parser.parse(self._value) if self._value else self._value


class BooleanField(AbstractField):
    false_values = ['0', 'false', 'f']

    def to_python(self) -> t.Optional[bool]:
        if self._value is None:
            return None

        if str(self._value).lower() in self.false_values:
            return False

        return True


# Todo: add other types
# Todo: add validators
# list
# date
# json
# Enum
# File
