import re
from typing import (
    Dict,
    Any,
    Optional,
)

from aiohttp import web
import aiohttp_jinja2
import sqlalchemy as sa

from aiohttp_admin2.views.base import (
    BaseAdminResourceView,
    BaseAdminView,
)
from aiohttp_admin2.types import (
    ListResult,
    ListParams,
)

__all__ = ['PostgresView', ]


class PostgresView(BaseAdminResourceView):
    """
    docs
    """
    template_name = 'admin/list.html'
    template_edit_name = 'admin/edit.html'
    template_create_name = 'admin/create.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        if self.title is BaseAdminView.title:
            self.title = re.sub(r'[_-]', ' ', self.Model.model.name)

    async def get_list(
        self,
        req: web.Request,
        params: ListParams,
    ) -> web.Response:
        async with self.engine(req).acquire() as conn:
            model = self.Model.model
            query = model\
                .select()\
                .limit(params.per_page)\
                .offset((params.page - 1) * params.per_page)\
                .order_by(sa.text(f'{params.sort} {params.sort_direction}'))

            cursor = await conn.execute(query)
            list_result = await cursor.fetchall()

            count_items = await conn.scalar(model.count())

            has_next = count_items / params.per_page - params.page > 0
            has_prev = params.page > 1

            return ListResult(
                list_result=list_result,
                active_page=params.page,
                count_items=count_items,
                has_next=has_next,
                has_prev=has_prev,
                per_page=params.per_page,
            )

    async def get_detail(self, req):
        async with self.engine(req).acquire() as conn:
            model = self.Model.model
            query = model\
                .select()\
                .where(model.c.user_id == req.match_info['id'])

            cursor = await conn.execute(query)

            return await cursor.fetchone()

    async def delete(self, req):
        async with self.engine(req).acquire() as conn:
            model = self.Model.model
            query = model.delete() \
                .where(model.c.user_id == req.match_info['id'])

            await conn.execute(query)
