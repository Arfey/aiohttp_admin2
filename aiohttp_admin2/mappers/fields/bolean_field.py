import typing as t

from aiohttp_admin2.mappers.fields.abc import AbstractField

__all__ = ["BooleanField", ]


class BooleanField(AbstractField):
    """
    A field for represent an boolean type:

    >>> from aiohttp_admin2.mappers import fields
    >>>
    >>> class Mapper(Mapper):
    >>>     field = fields.BooleanField()

    this fields convert any value which is not contains in `false_values` list
    to `True` and to `False` in other case.
    """
    type_name: str = 'boolean'
    false_values = ['0', 'false', 'f', '', 'none']

    def to_python(self) -> t.Optional[bool]:
        if self._value is None:
            return None

        if str(self._value).lower() in self.false_values:
            return False

        return True
