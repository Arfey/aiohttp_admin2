from typing import (
    Dict,
    Any,
    Optional,
    Union
)

import aiohttp_jinja2
from aiohttp import web
from aiohttp_admin2.core.forms import BaseForm
from  aiopg.sa.engine import Engine as SAEngine
import sqlalchemy as sa


__all__ = ['BaseAdminView', 'BaseAdminResourceView', ]


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
    changeable_attributes = [
        'read_only_fields',
        'engine',
        'Model',
        'get_context',
        'get_list',
        'template_name',
        'get_detail',
        'name'
    ]
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
        }

    def setup(
        self,
        admin: web.Application,
    ) -> None:
        # Generate simple view with params that can be change
        BaseView = type('BaseView', (web.View, ), {
                key: getattr(self, key)
                for key in self.changeable_attributes
            }
        )

        class ListView(BaseView):
            template_name = self.template_name

            async def get(self) -> web.Response:
                ctx = await self.get_context(self.request)
                ctx['list'] = await self.get_list(self.request)

                return aiohttp_jinja2.render_template(
                    self.template_name,
                    self.request,
                    ctx,
                )

        class EditView(BaseView):
            template_name = self.template_edit_name

            async def get(self) -> web.Response:
                ctx = await self.get_context(self.request)
                obj = await self.get_detail(self.request)
                ctx['obj'] = obj
                ctx['form'] = self.Model.form(obj).render_to_html()

                return aiohttp_jinja2.render_template(
                    self.template_name,
                    self.request,
                    ctx,
                )

            async def post(self) -> web.Response:
                data = await self.request.post()
                form = self.Model.form(data)

                if not form.is_valid():
                    ctx = await self.get_context(req)
                    obj = await self.get_detail(req)
                    ctx['obj'] = obj
                    ctx['form'] = self.Model.form(obj).render_to_html()

                    ctx['form'] = form.render_to_html()

                    return aiohttp_jinja2.render_template(
                        self.template_create_name,
                        req,
                        ctx,
                    )

                async with self.engine(self.request).acquire() as conn:
                    model = self.Model.model
                    query = model\
                        .update()\
                        .where(model.c.user_id == self.request.match_info['id'])\
                        .values(data)

                    cursor = await conn.execute(query)

                redirect = self.request.app.router[self.name].url_for()
                return web.HTTPFound(location=redirect)

        class CreateView(BaseView):
            template_name = self.template_create_name

            async def get(self) -> web.Response:
                ctx = await self.get_context(self.request)
                ctx['delete_url'] = f'{self.name}_delete'
                ctx['form'] = self.Model.form().render_to_html()

                return aiohttp_jinja2.render_template(
                    self.template_name,
                    self.request,
                    ctx,
                )
        
            async def post(self) -> web.Response:
                data = await self.request.post()
                form = self.Model.form(data)

                if not form.is_valid():
                    ctx = await self.get_context(self.request)
                    ctx['delete_url'] = f'{self.name}_delete'
                    ctx['form'] = form.render_to_html()

                    return aiohttp_jinja2.render_template(
                        self.template_create_name,
                        self.request,
                        ctx,
                    )
                
                async with self.engine(self.request).acquire() as conn:
                    model = self.Model.model
                    query = model\
                        .insert()\
                        .values(data)

                    cursor = await conn.execute(query)
                
                redirect = self.request.app.router[self.name].url_for()
                return web.HTTPFound(location=redirect)
        
        class DeleteView(BaseView):
            async def delete(self) -> web.Response:
                await self.delete(self.request)

                raise web.HTTPFound(self.request.app.router[self.name].url_for())


        admin.add_routes([
            web.view(
                self.index_url,
                ListView,
                name=self.name,
            ),
            web.view(
                '%screate/' % self.index_url,
                CreateView,
                name=f'{self.name}_create',
            ),
            web.view(
                '%s{id}/edit/' % self.index_url,
                EditView,
                name=f'{self.name}_edit',
            ),
            web.view(
                '%s{id}/delete/' % self.index_url,
                DeleteView,
                name=f'{self.name}_delete',
            )
        ])

    
    class Model:
        model = None
        form = None
