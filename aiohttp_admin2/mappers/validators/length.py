import typing as t

from aiohttp_admin2.mappers.exceptions import ValidationError

__all__ = ["length", ]


LengthCallable = t.Callable[[t.Sized], None]


def length(*, max_value: int = None, min_value: int = None) -> LengthCallable:
    """
    This validator need to restrict length of value in field.

        >>> from aiohttp_admin2.mappers import Mapper, StringField
        >>>
        >>> class Foo(Mapper):
        >>>     field_name = StringField(validators=[length(max_value=5)])
    """
    def length_validator(value: t.Sized) -> None:
        if max_value and len(value) > max_value:
            raise ValidationError(
                f"'{value}' has length larger than {max_value}"
            )

        if min_value and len(value) < min_value:
            raise ValidationError(
                f"'{value}' has length less than {min_value}"
            )

    return length_validator
