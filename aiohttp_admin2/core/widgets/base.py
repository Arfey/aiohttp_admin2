from typing import (
    Dict,
    Any,
    TYPE_CHECKING,
)

from aiohttp import web
from aiohttp_admin2.core.widgets.templates import SIMPLE_INPUT_TEMPALTE

if TYPE_CHECKING:
    from aiohttp_admin2.core.forms import BaseForm


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
    def render_to_html(cls, form: 'BaseForm') -> str:
        return cls.template.format(**cls.get_context(form))

    @classmethod
    def get_context(cls, form: 'BaseForm') -> Dict[str, Any]:
        return {
            'name': form.name,
            'type': cls.type_name,
            'value': form.value,
        }
