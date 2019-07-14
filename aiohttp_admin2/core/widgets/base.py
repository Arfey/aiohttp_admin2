from typing import (
    Dict,
    Any,
    TYPE_CHECKING,
)

from aiohttp import web
from aiohttp_admin2.core.widgets.templates import (
    SIMPLE_INPUT_TEMPALTE,
    ERROR,
)

if TYPE_CHECKING:
    from aiohttp_admin2.core.fields.abc import FieldABC


__all__ = ['Widget', ]


class Widget:
    """
    This class provide default behaviour of admin's widget. A widget is object
    that define view of field in html and all other stuff witch need for render
    a field.
    """
    template = SIMPLE_INPUT_TEMPALTE
    type_name = 'input'

    @classmethod
    def render_to_html(cls, field: 'FieldABC') -> str:
        return cls.template.format(**cls.get_context(field))

    @classmethod
    def get_context(cls, field: 'FieldABC') -> Dict[str, Any]:
        errors = ''
        if field.errors:
            errors = "".join([
                ERROR.format(err.message)
                for err in field.errors
            ])

        return {
            'name': field.name,
            'type': cls.type_name,
            'value': field.value,
            'errors': errors,
            'required': 'required="required"' if field.required else ''
        }
