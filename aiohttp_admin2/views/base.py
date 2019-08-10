from typing import (
    Dict,
    Any,
    Optional,
    Union,
    NamedTuple,
)

import aiohttp_jinja2
from aiohttp import web
from aiohttp.web_routedef import _SimpleHandler as Handler
from aiohttp_admin2.core.forms import BaseForm
from  aiopg.sa.engine import Engine as SAEngine
import sqlalchemy as sa



__all__ = ['BaseAdminView', 'BaseAdminResourceView', 'ListResult', ]


class ListResult(NamedTuple):
    list_result: list
    has_next: bool
    has_prev: bool
    active_page: int
    count_items: int
    per_page: int


class BaseAdminView:
    """
    The base class for all admin view.
    """
    index_url: str = None
    name: str = None
    title: str = 'None'
    icon: str = 'label'
    group_name: str = 'General'
    is_hide_view: bool = False

    def __init__(self) -> None:
        default = self.__class__.__name__.lower()
        self.index_url = self.index_url or f'/{default}/'
        self.name = self.name or default
        self.title = self.title if not self.title == 'None' else default

    def setup(self, app: web.Application) -> None:
        raise NotImplemented


class BaseAdminResourceView(BaseAdminView):
    """
    The base class for views which work with database.
    """
    read_only_fields = []
    inline_fields = []

    # CRUD access
    can_create = True
    can_update = True
    can_delete = True
    can_view_list = True
    per_page = 50

    def __init__(self) -> None:
        super().__init__()

        for field in ['model', 'form', 'engine_name']:
            if not hasattr(self.Model, field):
                raise TypeError(
                    f'Missing required property {field} in Model class.'
                )

        self._model: sa.Table  = self.Model.model
        self._form: BaseForm = self.Model.form
        self._engine: str = self.Model.engine_name

    def engine(self, req: web.Request) -> Union[SAEngine]:
        """
        The main convention about data sharing in aiohttp is that u need
        to use an application instance to share global variables. So,
        all database connection you need to save into an aiohttp
        instance for correct work of admin.

        Reference:
        https://docs.aiohttp.org/en/stable/web_advanced.html#data-sharing-aka-no-singletons-please
        """
        return req.config_dict[self._engine]

    @property
    def model(self) -> Union[sa.Table]:
        return self._model

    @property
    def form(self) -> BaseForm:
        return self._form

    async def get_context(self, req: web.Request):
        return {
            "request": req,
            'edit_url_name': f'{self.name}_edit',
            'create_url_name': f'{self.name}_create',
            "view": self,
        }

    async def list_handler(self, req) -> web.Response:
        ctx = await self.get_context(req)

        page = int(req.rel_url.query.get('page', 1))

        ctx['list'] = await self.get_list(
            req,
            page,
            self.per_page,
        )

        return aiohttp_jinja2.render_template(
            self.template_name,
            req,
            ctx,
        )

    async def edit_handler(self, req) -> web.Response:
        ctx = await self.get_context(req)
        obj = await self.get_detail(req)
        ctx['obj'] = obj
        ctx['form'] = self.Model.form(obj)
        ctx['delete_url'] = f'{self.name}_delete'

        return aiohttp_jinja2.render_template(
            self.template_edit_name,
            req,
            ctx,
        )

    async def edit_post_handler(self, req) -> web.Response:
        data = await req.post()
        form = self.Model.form(data)

        if not form.is_valid():
            ctx = await self.get_context(req)
            obj = await self.get_detail(req)
            ctx['obj'] = obj
            ctx['form'] = self.Model.form(obj)

            return aiohttp_jinja2.render_template(
                self.template_create_name,
                req,
                ctx,
            )

        async with self.engine(req).acquire() as conn:
            model = self.Model.model
            query = model\
                .update()\
                .where(model.c.user_id == req.match_info['id'])\
                .values(data)

            cursor = await conn.execute(query)

        redirect = req.app.router[self.name].url_for()
        return web.HTTPFound(location=redirect)


    async def create_handler(self, req) -> web.Response:
        ctx = await self.get_context(req)
        ctx['delete_url'] = f'{self.name}_delete'
        ctx['form'] = self.Model.form()

        return aiohttp_jinja2.render_template(
            self.template_create_name,
            req,
            ctx,
        )
    
    async def create_post_handler(self, req) -> web.Response:
        data = await req.post()
        form = self.Model.form(data)

        if not form.is_valid():
            ctx = await self.get_context(req)
            ctx['delete_url'] = f'{self.name}_delete'
            ctx['form'] = form

            return aiohttp_jinja2.render_template(
                self.template_create_name,
                req,
                ctx,
            )
        
        async with self.engine(req).acquire() as conn:
            model = self.Model.model
            query = model\
                .insert()\
                .values(data)

            cursor = await conn.execute(query)

        redirect = req.app.router[self.name].url_for()
        return web.HTTPFound(location=redirect)

    async def delete_handler(self, req) -> web.Response:
        await self.delete(req)

        raise web.HTTPFound(req.app.router[self.name].url_for())

    def access_hook(self):
        pass

    def _get_list(self, req):
        new_instance = self.__class__()
        new_instance.access_hook(req)

        if not self.can_view_list:
            raise web.HTTPForbidden()

        return new_instance.list_handler(req)


    def _create(self, req):
        new_instance = self.__class__()
        new_instance.access_hook(req)

        if not self.can_create:
            raise web.HTTPForbidden()

        if req.method == 'POST':
            return new_instance.create_post_handler(req)
        else:
            return new_instance.create_handler(req)

    def _update(self, req):
        new_instance = self.__class__()
        new_instance.access_hook(req)

        if not self.can_update:
            raise web.HTTPForbidden()
    
        if req.method == 'POST':
            return new_instance.edit_post_handler(req)
        else:
            return new_instance.edit_handler(req)

    def _delete(req):
        new_instance = self.__class__()
        new_instance.access_hook(req)

        if not self.can_delete:
            raise web.HTTPForbidden()

        return new_instance.delete_handler(req)

    def get_read_only_field(self, name: str, inst) -> str:
        return getattr(self, f'{name}_field')(inst)

    def setup(
        self,
        admin: web.Application,
    ) -> None:
        # each request must generate a new instance of class for give
        # possible to customize view for it
        

        admin.add_routes([
            web.get(
                self.index_url,
                self._get_list,
                name=self.name,
            ),
            web.get(
                '%screate/' % self.index_url,
                self._create,
                name=f'{self.name}_create',
            ),
            web.post(
                '%screate/' % self.index_url,
                self._create,
            ),
            web.get(
                '%s{id}/edit/' % self.index_url,
                self._update,
                name=f'{self.name}_edit',
            ),
            web.post(
                '%s{id}/edit/' % self.index_url,
                self._update,
            ),
            web.post(
                '%s{id}/delete/' % self.index_url,
                self._delete,
                name=f'{self.name}_delete',
            ),
        ])


    class Model:
        model = None
        form = None
