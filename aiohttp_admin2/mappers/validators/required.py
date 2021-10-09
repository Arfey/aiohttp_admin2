import typing as t

from aiohttp_admin2.mappers.exceptions import ValidationError

__all__ = ["required", ]


def required(value: t.Any):
    """
    This validator need for check that the received value is not empty.

        >>> from aiohttp_admin2.mappers import Mapper, StringField
        >>>
        >>> class Foo(Mapper):
        >>>     field_name = StringField(validators=[required])
        >>>     # or just
        >>>     second_field_name = StringField(required=True)
    """
    if value is None or value == '':
        raise ValidationError("field is required")
