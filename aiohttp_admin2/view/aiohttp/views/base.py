import typing as t
from aiohttp import web

from aiohttp_admin2.mappers import fields
from aiohttp_admin2 import widgets
from aiohttp_admin2 import filters
from aiohttp_admin2.view.aiohttp.views.utils import ViewUtilsMixin


__all__ = ['BaseAdminView', 'DEFAULT_TYPE_WIDGETS', 'DEFAULT_FILTER_MAP', ]


DEFAULT_TYPE_WIDGETS = {
    fields.StringField.type_name: widgets.StringWidget,
    fields.ChoicesField.type_name: widgets.ChoiceWidget,
    fields.BooleanField.type_name: widgets.BooleanWidget,
    fields.ArrayField.type_name: widgets.ArrayWidget,
    fields.DateTimeField.type_name: widgets.DateTimeWidget,
    fields.DateField.type_name: widgets.DateWidget,
    fields.JsonField.type_name: widgets.JsonWidget,
    fields.UrlFileField.type_name: widgets.FileWidget,
    fields.UrlImageField.type_name: widgets.ImageWidget,
    'autocomplete': widgets.AutocompleteStringWidget,
}
DEFAULT_FILTER_MAP = {
    fields.ChoicesField.type_name: filters.ChoiceFilter,
    fields.BooleanField.type_name: filters.BooleanFilter,
    fields.DateTimeField.type_name: filters.DateTimeFilter,
    fields.DateField.type_name: filters.DateFilter,
    fields.StringField.type_name: filters.SingleValueFilter,
    fields.UrlFileField.type_name: filters.SingleValueFilter,
    fields.UrlImageField.type_name: filters.SingleValueFilter,
    fields.IntField.type_name: filters.SingleValueFilter,
}


class BaseAdminView(ViewUtilsMixin):
    """
    The base class for all admin view.
    """
    index_url: str = None
    name: str = None
    title: str = 'None'
    icon: str = 'label'
    group_name: str = 'General'
    is_hide_view: bool = False

    # todo: docs
    fields_widgets = {}
    default_widget = widgets.StringWidget
    foreignkey_widget = widgets.AutocompleteStringWidget
    type_widgets = {}
    default_type_widgets = DEFAULT_TYPE_WIDGETS
    default_filter_map = DEFAULT_FILTER_MAP
    search_filter = filters.SearchFilter

    def __init__(self, *, params: t.Dict[str, t.Any] = None) -> None:
        default = self.__class__.__name__.lower()
        self.index_url = self.index_url or f'/{default}/'
        self.name = self.name or default
        self.title = self.title if not self.title == 'None' else default
        self.params = params or {}

    async def get_context(self, req: web.Request) -> t.Dict[str, t.Any]:
        """
        In this place you can redefine whole context which will use for
        generate custom page.
        """
        return {
            "request": req,
            "title": self.title,
            "controller_view": self,
            "type_of": type,
        }

    def setup(self, app: web.Application) -> None:
        raise NotImplemented
