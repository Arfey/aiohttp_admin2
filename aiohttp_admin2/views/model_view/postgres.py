import re
from typing import (
    Dict,
    Any,
    Optional,
)

from aiohttp import web
import aiohttp_jinja2

from aiohttp_admin2.views.base import (
    BaseAdminResourceView,
    BaseAdminView,
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

    async def get_list(self, req):
        async with self.engine(req).acquire() as conn:
            model = self.Model.model
            query = model\
                .select()\
                .order_by(model.c.user_id)

            cursor = await conn.execute(query)

            return await cursor.fetchall()

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
