import typing as t

from aiohttp import web


__all__ = ['get_params_from_request', 'QueryParams', 'get_field_value', ]


class QueryParams(t.NamedTuple):
    """
    # todo: description
    """
    page: t.Optional[int]
    cursor: t.Optional[int]
    order_by: t.Optional[str]


# todo: add test
def get_params_from_request(req: web.Request) -> QueryParams:
    """
    This function need for convert query string to filter parameters.
    """
    page = int(req.rel_url.query.get('page', '1'))
    cursor = req.rel_url.query.get('cursor')
    sort = req.rel_url.query.get('sort')
    sort_dir = req.rel_url.query.get('sortDir')

    if sort and sort_dir == 'desc':
        sort = f'-{sort}'

    return QueryParams(
        page=page,
        cursor=int(cursor) if cursor else None,
        order_by=sort,
    )


def get_field_value(field, with_defaults) -> str:
    """
    This helper need to extract value from field.
    """
    if field.is_not_none:
        return field.failure_safe_value
    elif field.default and with_defaults:
        return field.default

    return ''
