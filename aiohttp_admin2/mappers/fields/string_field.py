import typing as t

from aiohttp_admin2.mappers.fields.abc import AbstractField

__all__ = ["StringField", "LongStringField", ]


class StringField(AbstractField):
    type_name: str = 'string'

    def to_python(self) -> t.Optional[str]:
        return str(self._value) if self._value else self._value


class LongStringField(StringField):
    type_name: str = 'string_long'
