from typing import (
    Union,
)

__all__ = ['required', ]


def required(value: Union[str, int] = None) -> None:
    """
    This validator check if value is not empty.
    """
    assert value, "This field is required."
