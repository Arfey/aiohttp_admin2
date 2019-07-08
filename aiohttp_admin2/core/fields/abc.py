from abc import ABC
from typing import (
    Optional,
    List,
    Any,
)

from ..widgets.base import Widget
from ..validators import required as required_validator

__all__ = ['FieldABC', ]


class FieldABC(ABC):
    """
    Any admin's fields must inherit of this class because it show all required
    method which must provide by a field for success work in admin interface.
    """
    name = None
    _value = None

    def __init__(
        self,
        *,
        default=None,
        widget=Widget,
        required: bool = False,
    ) -> None:
        self.widget = widget
        self.default = default or self.default

    @property
    def value(self):
        return self._value or self.default

    # TODO: test
    @value.setter
    def value(self, value) -> None:
        self._value = value

    def render_to_html(self) -> str:
        return self.widget.render_to_html(self)
