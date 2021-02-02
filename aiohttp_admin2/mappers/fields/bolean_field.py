import typing as t

from aiohttp_admin2.mappers.fields.abc import AbstractField

__all__ = ["BooleanField", ]


class BooleanField(AbstractField):
    type_name: str = 'boolean'
    false_values = ['0', 'false', 'f', '', 'none']

    def to_python(self) -> t.Optional[bool]:
        if str(self._value).lower() in self.false_values:
            return False

        return True
