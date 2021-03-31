from aiohttp import web
import aiohttp_jinja2
import typing as t

from aiohttp_admin2.view.aiohttp.views.base import BaseAdminView
from aiohttp_admin2.view.aiohttp.views.tab_base_view import TabBaseView
from aiohttp_admin2.view.aiohttp.views.many_to_many_tab_view import \
    ManyToManyTabView
from aiohttp_admin2.controllers.relations import ToManyRelation
from aiohttp_admin2.resources.types import Instance
from aiohttp_admin2.controllers.controller import (
    Controller,
    DETAIL_NAME,
    FOREIGNKEY_DETAIL_NAME,
)
from aiohttp_admin2.mappers import Mapper


class ControllerView(BaseAdminView):
    """
    This class need for represent a pages based on controller for admin
    interface.
    """
    # Templates
    template_list_name = 'aiohttp_admin/layouts/list_page.html'
    template_list_cursor_name = 'aiohttp_admin/layouts/list_cursor_page.html'
    template_detail_name = 'aiohttp_admin/layouts/detail_view_page.html'
    template_detail_edit_name = 'aiohttp_admin/layouts/detail_edit_page.html'
    template_detail_create_name = 'aiohttp_admin/layouts/create_page.html'
    template_delete_name = 'aiohttp_admin/layouts/delete_page.html'

    controller: Controller
    _controller_instance: Controller = None
    tabs: t.List[TabBaseView] = None
    tabs_list: t.List[t.Any] = None

    def __init__(self, *, params: t.Dict[str, t.Any] = None) -> None:
        self.tabs_list = self.tabs_list or []
        self.tabs = self.tabs or []
        default = self.controller.name

        self.controller_url = self.controller.url_name()
        self.index_url = self.index_url or f'/{self.controller_url}/'
        self.name = self.name or default

        self.title = self.title if not self.title == 'None' else default
        self.params = params or {}

        for relation in self.controller.relations_to_many:
            relation.accept(self)

        if self.tabs:
            self.tabs_list = [Tab(self) for Tab in self.tabs]

        # todo: move to base and fix super
        self.common_type_widgets = {
            **self.default_type_widgets,
            **self.type_widgets
        }

    def get_extra_media(self):
        css = []
        js = []

        for w in {
            **self.default_type_widgets,
            **self.type_widgets,
            **self.fields_widgets,
        }.values():
            css.extend([link for link in w.css_extra if link not in css])
            js.extend([link for link in w.js_extra if link not in js])

        return dict(css=css, js=js)

    def get_extra_media_list(self):
        css = []
        js = []

        for w in {
            **self.default_filter_map
        }.values():
            css.extend([link for link in w.css_extra if link not in css])
            js.extend([link for link in w.js_extra if link not in js])

        return dict(css=css, js=js)

    # Urls
    @property
    def detail_url_name(self):
        return f'{self.controller_url}_detail'

    @property
    def create_url_name(self):
        return f'{self.controller_url}_create'

    @property
    def create_post_url_name(self):
        return f'{self.controller_url}_create_post'

    @property
    def update_post_url_name(self):
        return f'{self.controller_url}_update_post'

    @property
    def delete_url_name(self):
        return f'{self.controller_url}_delete'

    @property
    def delete_post_url_name(self):
        return f'{self.controller_url}_delete_post'

    def resolve_create_url(self, req: web.Request) -> str:
        return str(req.app.router[self.create_url_name].url_for())

    def resolve_create_post_url(self, req: web.Request) -> str:
        return str(req.app.router[self.create_post_url_name].url_for())

    @property
    def index_url_name(self):
        return self.controller_url

    def get_autocomplete_url(self, name: str) -> str:
        return f'/{self.index_url_name}/_autocomplete_{name}'

    def get_autocomplete_url_name(self, name: str) -> str:
        return f'{self.index_url_name}_autocomplete_{name}'

    def get_controller(self):
        if not self._controller_instance:
            self._controller_instance = self.controller\
                .builder_form_params(self.params)
        return self._controller_instance

    async def get_list(self, req: web.Request) -> web.Response:
        params = self.get_params_from_request(req)
        controller = self.get_controller()

        filters = self.get_list_filters(
            req,
            controller,
            self.default_filter_map,
        )

        def url_builder(obj: Instance, url_type: str, **kwargs) -> str:
            if url_type is DETAIL_NAME:
                return str(
                    req.app.router[self.detail_url_name]
                    .url_for(pk=str(obj.get_pk()))
                )
            elif url_type is FOREIGNKEY_DETAIL_NAME:
                url_name = kwargs.get('url_name')
                return str(
                    req.app.router[url_name + '_detail']
                        .url_for(
                            pk=str(obj.get_pk())
                        )
                    )

            return ''

        data = await controller.get_list(
            **params._asdict(),
            filters=filters,
            url_builder=url_builder,
        )

        with_infinity_scroll = bool(req.rel_url.query.get('cursor'))

        if with_infinity_scroll:
            template = self.template_list_cursor_name
        else:
            template = self.template_list_name

        # list_filter
        return aiohttp_jinja2.render_template(
            template,
            req,
            {
                **await self.get_context(req),
                "list": data,
                "controller": controller,
                "detail_url": self.detail_url_name,
                "create_url": self.resolve_create_url(req),
                "message": req.rel_url.query.get('message'),
                "media": self.get_extra_media_list(),
                "view_filters": self.get_filters(req.rel_url.query),
            }
        )

    async def get_detail(
        self,
        req: web.Request,
        mapper: t.Dict[str, t.Any] = None,
    ) -> web.Response:
        controller = self.get_controller()
        # todo: handle str key for dict
        pk = req.match_info['pk']
        data = await controller.get_detail(pk)

        template = self.template_detail_edit_name

        if not controller.can_update:
            template = self.template_detail_name

        return aiohttp_jinja2.render_template(
            template,
            req,
            {
                **await self.get_context(req),
                "media": self.get_extra_media(),
                "object": data,
                "controller": controller,
                "title": f"{self.name}#{data.id}",
                "delete_url": req.app.router[self.delete_url_name]
                    .url_for(pk=pk),
                "detail_url": req.app.router[self.detail_url_name]
                    .url_for(pk=pk),
                "save_url": req.app.router[self.update_post_url_name]
                    .url_for(pk=pk),
                "mapper": mapper or controller.mapper(data.__dict__),
                "fields": controller.fields,
                "message": req.rel_url.query.get('message'),
                "exclude_fields": self.controller.exclude_update_fields,
                "is_common": True,
                "tabs": self.tabs_list,
                "pk": pk,
            }
        )

    async def get_create(
        self,
        req: web.Request,
        mapper: t.Dict[str, t.Any] = None,
    ) -> web.Response:
        controller = self.get_controller()

        return aiohttp_jinja2.render_template(
            self.template_detail_create_name,
            req,
            {
                **await self.get_context(req),
                "media": self.get_extra_media(),
                "controller": controller,
                "title": f"Create a new {self.name}",
                "mapper": mapper or controller.mapper({}),
                "fields": controller.fields,
                "exclude_fields": self.controller.exclude_create_fields,
                "create_post_url": self.resolve_create_post_url(req)
            }
        )

    async def post_create(self, req: web.Request) -> web.Response:
        controller = self.get_controller()
        data = dict(await req.post())

        obj = await controller.create(data)

        if isinstance(obj, Mapper):
            return await self.get_create(req, obj)
        else:
            raise web.HTTPFound(
                req.app.router[self.detail_url_name]
                    .url_for(pk=str(obj.id))
                    .with_query(
                    f'message=The {self.name}#{obj.id} has been created'
                )
            )

    # todo: concat post and get update
    async def post_update(self, req: web.Request) -> web.Response:
        controller = self.get_controller()
        data = dict(await req.post())
        # todo: get_pk_name
        pk = req.match_info['pk']

        obj = await controller.update(pk, data)

        if isinstance(obj, Mapper):
            return await self.get_detail(req, obj)
        else:
            raise web.HTTPFound(
                req.app.router[self.detail_url_name]
                    .url_for(pk=pk)
                    .with_query(
                    f'message=The {self.name}#{pk} has been updated'
                )
            )

    async def get_delete(self, req: web.Request) -> web.Response:
        pk = req.match_info['pk']
        controller = self.get_controller()

        return aiohttp_jinja2.render_template(
            self.template_delete_name,
            req,
            {
                **await self.get_context(req),
                "title": f"Confirm delete {self.name}#{pk}",
                "controller": controller,
                "delete_url": req.app.router[self.delete_post_url_name]
                    .url_for(pk=pk),
                "pk": pk,
            }
        )

    async def post_delete(self, req: web.Request) -> None:
        controller = self.get_controller()
        pk = req.match_info['pk']
        await controller.delete(int(pk))
        location = req.app.router[self.index_url_name]\
            .url_for()\
            .with_query(f'message=The {self.name}#{pk} has been deleted')
        raise web.HTTPFound(location=location)

    def setup(self, app: web.Application) -> None:
        app.add_routes([
            web.get(
                self.index_url,
                self.get_list,
                name=self.index_url_name,
            ),
            web.get(
                f'{self.index_url}' + r'{pk:\w+}',
                self.get_detail,
                name=self.detail_url_name,
            ),
            web.get(
                f'{self.index_url}' + 'create/',
                self.get_create,
                name=self.create_url_name,
            ),
            web.get(
                f'{self.index_url}' + r'{pk:\w+}/delete',
                self.get_delete,
                name=self.delete_url_name,
            ),
            web.post(
                f'{self.index_url}' + r'{pk:\w+}/delete',
                self.post_delete,
                name=self.delete_post_url_name,
            ),
            web.post(
                f'{self.index_url}' + r'create_post/',
                self.post_create,
                name=self.create_post_url_name,
            ),
            web.post(
                f'{self.index_url}' + r'{pk:\w+}/update_post',
                self.post_update,
                name=self.update_post_url_name,
            ),
        ])

        for tab in self.tabs_list:
            tab.setup(app)

        controller = self.get_controller()

        # autocomplete
        autocomplete_routes = []
        for name, relation in controller.foreign_keys_field_map.items():
            async def autocomplete(req):
                return web.json_response([])

            autocomplete_routes.append(web.get(
                self.get_autocomplete_url(name),
                autocomplete,
                name=self.get_autocomplete_url_name(name)
            ))

        app.add_routes(autocomplete_routes)

    def visit_to_many_relations(self, obj: ToManyRelation) -> None:
        tab = type(
            f'{self.__class__.__name__}ManyToManyTab',
            (ManyToManyTabView,),
            {
                "name": obj.name,
                "controller": obj.relation_controller,
                "left_table_name": obj.left_table_pk,
                "right_table_name": obj.right_table_pk,
            }
        )

        self.tabs.append(tab)
