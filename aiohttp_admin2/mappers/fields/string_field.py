import typing as t

from aiohttp_admin2.mappers.fields.abc import AbstractField

__all__ = ["StringField", "LongStringField", ]


class StringField(AbstractField):
    """
    This class represent simple string type.
    """
    type_name: str = 'string'

    def to_python(self) -> t.Optional[str]:
        return str(self._value) if self._value is not None else self._value


class LongStringField(StringField):
    """
    This class represent simple string type but have different representation
    in the admin interface (more space for text).
    """
    type_name: str = 'string_long'
