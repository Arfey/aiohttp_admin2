from dateutil import parser
from datetime import datetime

from aiohttp_admin2.mappers.fields.abc import AbstractField, EmptyValue


# todo: default




class StringField(AbstractField):

    def to_python(self) -> str:
        return str(self._value)

    def to_raw(self) -> str:
        return str(self._value)


class IntField(AbstractField):

    def to_python(self) -> int:
        return int(self._value)

    def to_raw(self) -> int:
        return int(self._value)


class FloatField(AbstractField):

    def to_python(self) -> float:
        return float(self._value)

    def to_raw(self) -> float:
        return float(self._value)


class DateTime(AbstractField):
    # todo: make a smart
    def to_python(self) -> datetime:
        return parser(self._value)

    def to_raw(self) -> str:
        return str(self._value)


class BooleanField(AbstractField):
    false_values = [
        '0',
        'false',
        'f',
    ]

    def to_python(self) -> bool:

        if str(self._value).lower() in self.false_values:
            return False

        return True

    def to_raw(self) -> str:
        return str(self._value)


# Todo: add other types
# Todo: add validators
# list
# datetime
# date
# json
# Enum
