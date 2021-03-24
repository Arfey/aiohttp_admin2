import typing as t

from aiohttp import web
from aiohttp_admin2.mappers import fields
from aiohttp_admin2 import widgets
from aiohttp_admin2 import filters
from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.filters import (
    FilerBase,
    SearchFilter,
)
from aiohttp_admin2.mappers.fields.abc import AbstractField
from aiohttp_admin2.view.aiohttp.utils import (
    get_params_from_request,
    QueryParams,
)
from aiohttp_admin2.resources.types import FilterTuple


__all__ = ['ViewUtilsMixin', 'DEFAULT_TYPE_WIDGETS', 'DEFAULT_FILTER_MAP', ]


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


# todo: tests
def get_list_filters(
    req: web.Request,
    controller: Controller,
    filter_mapper: t.Dict[str, t.Any],
) -> t.List[FilerBase]:
    """
    In this function we extract filter from request params and return
    represented as list of internal classes.
    """
    filters = []

    for f in controller.list_filter:
        field = controller.mapper({})._fields[f]
        filter_cls = filter_mapper.get(field.type_name)
        if filter_cls:
            filters_list = filter_cls(field, req.rel_url.query) \
                .get_filter_list()

            if filters_list:
                filters.extend(filters_list)

    if controller.search_fields:
        filters.extend(
            SearchFilter(controller.search_fields, req.rel_url.query)
                .get_filter_list()
        )

    return filters


class ViewUtilsMixin:
    """
    We mixin class instead of separate functions because it's easier to
    rewrite then use monkeypatch for end user.
    """

    fields_widgets = {}
    default_widget = widgets.StringWidget
    foreignkey_widget = widgets.AutocompleteStringWidget
    type_widgets = {}
    common_type_widgets = {}
    default_type_widgets = DEFAULT_TYPE_WIDGETS
    default_filter_map = DEFAULT_FILTER_MAP
    search_filter = filters.SearchFilter

    @staticmethod
    def get_params_from_request(req: web.Request) -> QueryParams:
        return get_params_from_request(req)

    @staticmethod
    def get_list_filters(
        req: web.Request,
        controller: Controller,
        filter_mapper: t.Dict[str, t.Any],
    ) -> t.List[t.Union[FilerBase, FilterTuple]]:
        """
        In this method we extract filter from request params and return
        represented as list of internal classes.
        """
        return get_list_filters(req, controller, filter_mapper)

    def get_filters(self, query) -> t.List[t.Tuple[str, FilerBase]]:
        controller = self.get_controller()
        empty_mapper = controller.mapper({})

        filters = []

        for f in controller.list_filter:
            field = empty_mapper._fields.get(f)
            filter_cls = self.default_filter_map.get(field.type_name)

            if filter_cls:
                filters.append((f, filter_cls(field, query)))
        return filters

    def get_widget_template_for_field(
        self,
        name: str,
        field_type: str,
    ) -> str:
        foreign_key_controller = self\
            .get_controller()\
            .foreign_keys_field_map.get(name)

        if (
            foreign_key_controller
            and foreign_key_controller.controller.with_autocomplete()
        ):
            widget = self.foreignkey_widget
        else:
            widget = self.fields_widgets.get(name)

            if not widget:
                widget = self.common_type_widgets\
                    .get(field_type, self.default_widget)

        return widget.template_name

