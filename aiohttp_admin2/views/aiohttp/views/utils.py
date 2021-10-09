import typing as t

from aiohttp import web
from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.exceptions import AdminException
from aiohttp_admin2.views.filters import FilerBase
from aiohttp_admin2.views.filters import SearchFilter


__all__ = [
    'route',
    'get_route',
    'IsNotRouteAdminException',
    'UrlInfo',
    'get_list_filters',
]


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


class RouteValidationAdminException(AdminException):
    pass


class IsNotRouteAdminException(AdminException):
    pass


class RouteInfo(t.NamedTuple):
    url: str
    method: str


class UrlInfo(t.NamedTuple):
    name: str
    url: str


def route(url: str, method='GET'):
    """
    :param url:
    :param method:
    :return:
    """
    method = method.upper()
    valid_methods = ['POST', 'GET', 'PUT', 'DELETE', 'HEAD', ]
    if method not in valid_methods:
        raise RouteValidationAdminException(
            f"The http method {method} is not valid because not contains in"
            f"list of valid methods {valid_methods}"
        )

    if not url.startswith('/') or not url.endswith('/'):
        raise RouteValidationAdminException(
            f"The url `f{url}` have to start and end by `/` symbol.")

    def inner(fn):
        fn.route = RouteInfo(url=url, method=method)
        return fn

    return inner


def get_route(fn) -> t.Optional[RouteInfo]:
    return getattr(fn, 'route', None)
