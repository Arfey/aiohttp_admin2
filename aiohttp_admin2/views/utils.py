from aiohttp import web

from aiohttp_admin2.types import (
    ListParams,
    SortDirectionEnum,
)


__all__ = ['getListParams', ]


def getListParams(req: web.Request, per_page: int = 50) -> ListParams:
    """
    Generate ListParams from request query.
    """
    return ListParams(
        page=int(req.rel_url.query.get('page', 1)),
        sort=req.rel_url.query.get('sort', 'user_id'),
        per_page=per_page,
        sort_direction=(
            req.rel_url.query.get('sortDir', SortDirectionEnum.ASC.value)
        ),
    )
