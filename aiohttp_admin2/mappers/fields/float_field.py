import typing as t

from aiohttp_admin2.mappers.fields.abc import AbstractField
from aiohttp_admin2.mappers.exceptions import ValidationError

__all__ = ["FloatField", ]


class FloatField(AbstractField):
    """
    Simple representation of float type.
    """
    type_name: str = 'float'

    def to_python(self) -> t.Optional[float]:
        try:
            return (
                float(self._value) if self._value is not None else self._value
            )
        except ValueError:
            raise ValidationError(
                f"Incorrect value for Float field. {self._value}"
            )
