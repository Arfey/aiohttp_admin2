import typing as t

from aiohttp_admin2.mappers.fields.abc import AbstractField

__all__ = ["FloatField", ]


class FloatField(AbstractField):
    type_name: str = 'float'

    def to_python(self) -> t.Optional[float]:
        return float(self._value) if self._value else self._value
