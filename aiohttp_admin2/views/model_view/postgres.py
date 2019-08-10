import re
from typing import (
    Dict,
    Any,
    Optional,
)

from aiohttp import web
import aiohttp_jinja2
from sqlalchemy import func

from aiohttp_admin2.views.base import (
    BaseAdminResourceView,
    BaseAdminView,
)

__all__ = ['PostgresView', ]


from typing import NamedTuple


class ListResult(NamedTuple):
    list_result: list
    has_next: bool
    has_prev: bool
    active_page: int
    count_items: int
    per_page: int


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
        page: int = 1,
        per_page: int = 50,
    ):
        async with self.engine(req).acquire() as conn:
            model = self.Model.model
            query = model\
                .select()\
                .limit(per_page)\
                .offset((page - 1) * per_page)\
                .order_by(model.c.user_id)

            cursor = await conn.execute(query)

            list_result = await cursor.fetchall()

            count_query = model.count()

            count_cursor = await conn.execute(count_query)

            count_items = await count_cursor.fetchone()

            has_next = count_items[0] / per_page - page > 0
            has_prev = page > 1

            return ListResult(
                list_result=list_result,
                active_page=page,
                count_items=count_items[0],
                has_next=has_next,
                has_prev=has_prev,
                per_page=per_page,
            )

    async def get_detail(self, req):
        async with self.engine(req).acquire() as conn:
            model = self.Model.model
            query = model \
                .select() \
                .where(model.c.user_id == req.match_info['id'])

            cursor = await conn.execute(query)

            return await cursor.fetchone()

    async def delete(self, req):
        async with self.engine(req).acquire() as conn:
            model = self.Model.model
            query = model.delete() \
                .where(model.c.user_id == req.match_info['id'])

            await conn.execute(query)
