from typing import NamedTuple

__all__ = ['Error', ]


class Error(NamedTuple):
    """
    docs
    """
    name: str = '__unknown__'
    text: str = ''
