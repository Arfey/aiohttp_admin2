import typing as t

from aiohttp import web
from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.filters import (
    FilerBase,
    SearchFilter,
)
from aiohttp_admin2.view.aiohttp.utils import (
    get_params_from_request,
    QueryParams,
)
from aiohttp_admin2.resources.types import FilterTuple


__all__ = ['ViewUtilsMixin']


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
            filters_list = filter_cls(f, req.rel_url.query) \
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
