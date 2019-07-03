from .abc import FieldABC

__all__ = ['TextField', ]


class TextField(FieldABC):
    """
    The base field for representation a text data.
    """
    default = ''
