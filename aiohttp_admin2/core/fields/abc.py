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

    def __init__(
        self,
        *,
        widget=Widget,
        required: bool = False,
    ) -> None:
        self.widget = widget
        self.validators = validators or []

        if required:
            self.validators.append(required_validator)
