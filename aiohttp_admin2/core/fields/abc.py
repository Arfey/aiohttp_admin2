from abc import ABC
from typing import (
    Optional,
    List,
    Any,
)

from aiohttp_admin2.core.widgets.base import Widget
from aiohttp_admin2.core.constants import (
    FormError,
    REQUIRED_CODE_ERROR,
    REQUIRED_MESSAGE_ERROR
)


__all__ = ['FieldABC', ]


class FieldABC(ABC):
    """
    Any admin's fields must inherit of this class because it show all required
    method which must provide by a field for success work in admin interface.
    """
    name = None
    required_message = REQUIRED_MESSAGE_ERROR
    required_code = REQUIRED_CODE_ERROR
    errors: List[FormError] = []

    def __init__(
        self,
        *,
        default=None,
        widget=Widget,
        required: bool = False,
    ) -> None:
        self._value = None
        self.widget = widget
        self.default = default or self.default
        self.required = required

    @property
    def value(self):
        return self._value or self.default

    def _set_value(self, value: str) -> None:
        self._value = value

    def render_to_html(self) -> str:
        """
        Generate html representation for field.
        """
        return self.widget.render_to_html(self)

    def is_required(self) -> Optional[FormError]:
        if self.required and not self.value:
            return FormError(
                message=self.required_message,
                code=self.required_code,
            )

        return None

    def validation(self) -> Optional[FormError]:
        """
        This method is needed to get a way to add a custom validation for
        the field.
        """
        pass
    
    @property
    def is_valid(self) -> bool:
        """
        The main method for check if form is valid.
        """
        self.errors = [
            err
            for err in [self.validation(), self.is_required()]
            if err
        ]

        return not len(self.errors)
