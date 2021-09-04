import typing as t

from aiohttp_admin2.mappers.exceptions import ValidationError
from aiohttp_admin2.mappers.fields.abc import AbstractField

__all__ = ["IntField", "SmallIntField", ]


class IntField(AbstractField):
    """
    Simple representation of float type.
    """
    type_name: str = 'int'

    def to_python(self) -> t.Optional[int]:
        if self._value == '':
            return None
        try:
            return int(self._value) if self._value is not None else self._value
        except ValueError:
            raise ValidationError(
                f"Incorrect value for Int field. {self._value}"
            )


class SmallIntField(IntField):
    """
    Simple representation of float type but with additional validation related
    with long of integer (only for int from MIN_INT to MAX_INT).
    """
    type_name: str = 'small_int'
    MAX_INT = 32_767
    MIN_INT = -32_768

    def to_python(self) -> t.Optional[int]:
        value = super().to_python()

        if value and (self.MIN_INT > value or value > self.MAX_INT):
            raise ValidationError(
                f"Value of SmallInt field have to between {self.MIN_INT} and "
                f"{self.MAX_INT} but received {value}"
            )

        return value
