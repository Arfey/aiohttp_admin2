from typing import (
    Dict,
    Any,
    Optional,
)

from aiohttp import web
import aiohttp_jinja2

from ..base import BaseAdminView


class PGModelView(BaseAdminView):
    """
    docs
    """
    template_name = 'admin/list.html'
    template_edit_name = 'admin/edit.html'

    async def get_list(self, req):
        async with self.get_engine(req.app['parent']).acquire() as conn:
            model = self.Meta.model
            query = model\
                .select()\
                .order_by(model.c.user_id)

            cursor = await conn.execute(query)

            return await cursor.fetchall()

    async def get_detail(self, req):
        async with self.get_engine(req.app['parent']).acquire() as conn:
            model = self.Meta.model
            query = model \
                .select() \
                .where(model.c.user_id == req.match_info['id'])

            cursor = await conn.execute(query)

            return await cursor.fetchone()

    async def delete(self, req):
        async with self.get_engine(req.app['parent']).acquire() as conn:
            model = self.Meta.model
            query = model.delete() \
                .where(model.c.user_id == req.match_info['id'])

            await conn.execute(query)

    async def get_context(self, req: web.Request):
        return {"request": req, 'edit_url_name': f'{self.name}_edit'}

    def get_engine(self, app):
        raise NotImplemented

    def setup(
        self,
        admin: web.Application,
    ) -> None:

        @aiohttp_jinja2.template(template_name=self.template_name)
        async def handler(req: web.Request) -> Dict[str, Any]:
            ctx = await self.get_context(req)
            ctx['list'] = await self.get_list(req)
            return ctx

        admin.add_routes([web.get(self.index_url, handler, name=self.name)])

        @aiohttp_jinja2.template(template_name=self.template_edit_name)
        async def edit_handler(req: web.Request) -> Dict[str, Any]:
            ctx = await self.get_context(req)
            ctx['obj'] = await self.get_detail(req)
            ctx['delete_url'] = f'{self.name}_delete'
            return ctx

        admin.add_routes([web.get('%s{id}/edit/' % self.index_url, edit_handler, name=f'{self.name}_edit')])

        async def delete_handler(req: web.Request):
            await self.delete(req)

            raise web.HTTPFound(req.app.router[self.name].url_for())

        admin.add_routes([web.post('%s{id}/delete/' % self.index_url,
                                  delete_handler, name=f'{self.name}_delete')])



    class Meta:
        engine = None
        engine_name: Optional[str] = None
        model = None
