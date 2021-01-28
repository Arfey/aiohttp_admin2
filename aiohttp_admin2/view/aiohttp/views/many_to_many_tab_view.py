import typing as t

import aiohttp_jinja2
from aiohttp import web

from .tab_template_view import TabTemplateView
from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2 import widgets
from aiohttp_admin2.resources.types import FilterTuple
from aiohttp_admin2 import filters
from aiohttp_admin2.view.aiohttp.views.utils import ViewUtilsMixin
from aiohttp_admin2.view.aiohttp.views.base import (
    DEFAULT_FILTER_MAP,
    DEFAULT_TYPE_WIDGETS,
)


__all__ = ['ManyToManyTabView', ]


# todo: nested from controller
class ManyToManyTabView(ViewUtilsMixin, TabTemplateView):
    controller: Controller
    template_detail_create_name = 'aiohttp_admin/create_mtm.html'
    template_detail_name = 'aiohttp_admin/detail_mtm.html'
    template_name: str = 'aiohttp_admin/template_tab_view_m2m.html'
    fields_widgets = {}
    default_widget = widgets.StringWidget
    type_widgets = {}
    default_type_widgets = DEFAULT_TYPE_WIDGETS
    default_filter_map = DEFAULT_FILTER_MAP
    search_filter = filters.SearchFilter
    left_table_name: str
    right_table_name: str

    # Fields
    exclude_fields = ['id', ]

    def get_controller(self):
        return self.controller.builder_form_params({})

    @property
    def create_url_name(self):
        return self.index_url_name + '_create'

    @property
    def create_post_url_name(self):
        return self.index_url_name + '_create_post'

    @property
    def delete_url_name(self):
        return self.index_url_name + '_delete'

    @property
    def detail_url_name(self):
        return self.index_url_name + '_detail'

    def setup(self, app: web.Application) -> None:
        app.add_routes([
            web.get(self.index_url, self.get_list, name=self.index_url_name),
            web.get(self.index_url + '/create', self.get_create, name=self.create_url_name),
            web.post(self.index_url + '/create_post', self.post_create, name=self.create_post_url_name),
            web.get(self.index_url + '/detail/{nested_pk:\w+}', self.get_detail, name=self.detail_url_name),
            web.post(self.index_url + '/detail/{nested_pk:\w+}', self.post_delete, name=self.delete_url_name),
        ])

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
                "media": [],
                "controller": controller,
                "title": f"Create a new {self.name}",

                "mapper": mapper or controller.mapper({
                    self.left_table_name: self.get_pk(req)
                }),
                "fields": controller.fields,
                "exclude_fields": self.exclude_fields,
                "create_url": self.create_post_url_name,
            }
        )

    async def post_create(self, req: web.Request) -> web.Response:
        controller = self.get_controller()
        data = dict(await req.post())
        data['id'] = -1

        mapper = controller.mapper(data)

        if mapper.is_valid():
            serialize_data = mapper.data
            del serialize_data['id']
            obj = await controller.create(serialize_data)

            raise web.HTTPFound(
                req.app.router[self.index_url_name]
                    .url_for(pk=self.get_pk(req))
                    .with_query(
                    f'message=The {self.name}#{obj.id} has been created'
                )
            )
        else:
            return await self.get_create(req, mapper)

    async def get_list(self, req: web.Request) -> web.Response:
        params = self.get_params_from_request(req)
        controller = self.get_controller()
        filters_list = self.get_list_filters(
            req,
            controller,
            self.default_filter_map,
        )
        filters_list.append(FilterTuple(
            self.left_table_name,
            self.get_pk(req),
            'eq',
        ))

        data = await controller.get_list(**params._asdict(), filters=filters_list)

        return aiohttp_jinja2.render_template(
            self.template_name,
            req,
            {
                **await self.get_context(req),
                'title': f"{self.parent.name}#{self.get_pk(req)}",
                'list': data,
                'content': await self.get_content(req),
                "controller": controller,
                "create_url": self.create_url_name,
                "detail_nested_url": self.delete_url_name,
            },
        )

    async def get_detail(
        self,
        req: web.Request,
        mapper: t.Dict[str, t.Any] = None,
    ) -> web.Response:
        controller = self.get_controller()
        data = await controller.get_detail(req.match_info['nested_pk'])

        return aiohttp_jinja2.render_template(
            self.template_detail_name,
            req,
            {
                **await self.get_context(req),
                "object": data,
                "controller": controller,
                "title": f"{self.name}#{data.id}",
                "pk": self.get_pk(req),
                "nested_pk": req.match_info['nested_pk'],
                "delete_url": self.delete_url_name,
                "mapper": mapper or controller.mapper(data.__dict__),
                "fields": controller.fields,
            }
        )

    async def post_delete(self, req: web.Request) -> None:
        controller = self.get_controller()
        pk = req.match_info['nested_pk']
        await controller.delete(int(pk))
        location = req.app.router[self.index_url_name] \
            .url_for(pk=self.get_pk(req)) \
            .with_query(f'message=The {self.name}#{pk} has been deleted')
        raise web.HTTPFound(location=location)
