import typing as t

from aiohttp_admin2.mappers.exceptions import ValidationError
from aiohttp_admin2.mappers.fields.abc import AbstractField

__all__ = ["IntField", ]


class IntField(AbstractField):
    type_name: str = 'int'

    def to_python(self) -> t.Optional[int]:
        try:
            return int(self._value) if self._value else self._value
        except ValueError:
            raise ValidationError(
                f"Incorrect value for Int field. {self._value}"
            )
