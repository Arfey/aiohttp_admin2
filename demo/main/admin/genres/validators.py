from aiohttp_admin2.mappers.exceptions import ValidationError

__all__ = ["validate_short_name", ]


def validate_short_name(val):
    if len(val) < 3:
        raise ValidationError("length too small")
