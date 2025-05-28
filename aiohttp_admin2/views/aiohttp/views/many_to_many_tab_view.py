import typing as t

import aiohttp_jinja2
from aiohttp import web
from aiohttp_admin2.controllers.controller import DETAIL_NAME
from aiohttp_admin2.controllers.controller import FOREIGNKEY_DETAIL_NAME
from aiohttp_admin2.mappers import Mapper
from aiohttp_admin2.resources.types import FilterTuple
from aiohttp_admin2.resources.types import Instance
from aiohttp_admin2.views.aiohttp.views.base import BaseControllerView
from aiohttp_admin2.views.aiohttp.views.base import global_views_instance
from aiohttp_admin2.views.aiohttp.views.tab_base_view import TabBaseView
from aiohttp_admin2.views.aiohttp.views.utils import route

__all__ = ['ManyToManyTabView', ]


class ManyToManyTabView(TabBaseView, BaseControllerView):

    left_table_pk_name: str

    # we need to drop `get` method from the BaseControllerView class
    get = None

    def get_detail_url(self):
        return self.get_url(self.get_detail).name

    async def access_hook(self) -> None:
        await super().access_hook()
        relations = self.get_controller().relations_to_one
        controller = self.get_controller()

        for relation in relations:
            # if any of relations controller has not access to read than all
            # many to many views are not available too
            relation_controller = relation.controller.builder()

            if not relation_controller.can_view:
                controller.can_view = False

            if not relation_controller.can_create:
                controller.can_create = False

            if not relation_controller.can_update:
                controller.can_update = False

    @route('/create/')
    async def get_create(
        self,
        req: web.Request,
        mapper: t.Dict[str, t.Any] = None,
    ) -> web.Response:
        pk = self.get_pk(req)
        controller = self.get_controller()
        create_post_url = req.app.router[self.get_url(self.post_create).name]\
            .url_for(pk=pk)
        mapper = mapper or controller.mapper({self.left_table_pk_name: pk})

        return aiohttp_jinja2.render_template(
            self.template_detail_create_name,
            req,
            {
                **await self.get_context(req),
                "media": self.get_extra_media(),
                "controller": controller,
                "title": f"Create a new {self.get_name()}",
                "mapper": mapper,
                "fields": controller.fields,
                "exclude_fields": self.controller.exclude_create_fields,
                "read_only_fields": self.controller.read_only_fields,
                "create_post_url": create_post_url,
            }
        )

    @route('/post_create/', method='POST')
    async def post_create(self, req: web.Request) -> web.Response:
        controller = self.get_controller()
        data = dict(await req.post())

        obj = await controller.create(data)

        if isinstance(obj, Mapper):
            return await self.get_create(req, obj)
        else:
            raise web.HTTPFound(
                req.app.router[self.get_index_url_name()]
                .url_for(pk=self.get_pk(req))
                .with_query(
                    f'message=The {self.get_name()}#{obj.get_pk()} '
                    f'has been created'
                )
            )

    @route(r'/update/{nested_pk:\w+}/', method='POST')
    async def post_update(self, req: web.Request) -> web.Response:
        controller = self.get_controller()
        data = dict(await req.post())
        pk = req.match_info['pk']
        nested_pk = req.match_info['nested_pk']

        obj = await controller.update(nested_pk, data)

        if isinstance(obj, Mapper):
            return await self.get_detail(req, obj)
        else:
            raise web.HTTPFound(
                req.app.router[self.get_url(self.get_detail).name]
                .url_for(pk=pk, nested_pk=nested_pk)
                .with_query(
                    f'message=The {self.get_name()}#{nested_pk} '
                    f'has been updated'
                )
            )

    @route(r'/')
    async def get_list(self, req: web.Request) -> web.Response:
        params = self.get_params_from_request(req)
        controller = self.get_controller()
        filters_list = self.get_list_filters(
            req,
            controller,
            self.default_filter_map,
        )
        filters_list.append(FilterTuple(
            self.left_table_pk_name,
            self.get_pk(req),
            'eq',
        ))

        url_name_maps = {
            i.get_controller().url_name(): i.get_detail_url()
            for i in global_views_instance.get() or []
            if hasattr(i, 'controller')
        }

        def url_builder(obj: Instance, url_type: str, **kwargs) -> str:
            if url_type is DETAIL_NAME:
                return str(
                    req.app.router[self.get_url(self.get_detail).name]
                    .url_for(
                        nested_pk=str(obj.get_pk()),
                        pk=req.match_info['pk']
                    )
                )
            elif url_type is FOREIGNKEY_DETAIL_NAME:
                url_name = kwargs.get('url_name')

                if url_name_maps.get(url_name):
                    return str(
                        req.app.router[url_name_maps.get(url_name)]
                        .url_for(pk=str(obj.get_pk()))
                    )

            return ''

        data = await controller.get_list(
            **params._asdict(),
            filters=filters_list,
            url_builder=url_builder,
            with_count=not self.infinite_scroll,
        )

        parent = self.get_parent()()

        return aiohttp_jinja2.render_template(
            self.template_list_name,
            req,
            {
                **await self.get_context(req),
                'title': f"{parent.get_name()}#{self.get_pk(req)}",
                'list': data,
                "controller": controller,
                "tabs": parent.tabs_list(),
                "detail_url": (
                    req.app.router[parent.get_url(parent.get_detail).name]
                    .url_for(pk=req.match_info['pk'])
                ),
                "create_url": (
                    req.app.router[self.get_url(self.get_create).name]
                    .url_for(pk=req.match_info['pk'])
                ),
                "view_filters": self.get_filters(req.rel_url.query),
            },
        )

    @route(r'/detail/{nested_pk:\w+}/')
    async def get_detail(
        self,
        req: web.Request,
        mapper: t.Dict[str, t.Any] = None,
    ) -> web.Response:
        pk = self.get_pk(req)
        controller = self.get_controller()
        nested_pk = req.match_info['nested_pk']
        instance = await controller.get_detail(req.match_info['nested_pk'])

        template = self.template_detail_edit_name

        if not controller.can_update:
            template = self.template_detail_name

        return aiohttp_jinja2.render_template(
            template,
            req,
            {
                **await self.get_context(req),
                "object": instance,
                "media": self.get_extra_media(),
                "exclude_fields": self.controller.exclude_update_fields,
                "read_only_fields": self.controller.read_only_fields,
                "controller": controller,
                "title": f"{self.get_name()}#{pk}",
                "pk": pk,
                "nested_pk": req.match_info['nested_pk'],
                "delete_url": (
                    req.app.router[self.get_url(self.get_delete).name]
                    .url_for(pk=pk, nested_pk=nested_pk)
                ),
                "detail_url": (
                    req.app.router[self.get_url(self.get_detail).name]
                    .url_for(pk=pk, nested_pk=nested_pk)
                ),
                "save_url": (
                    req.app.router[self.get_url(self.post_update).name]
                    .url_for(pk=pk, nested_pk=nested_pk)
                ),
                "mapper": mapper or controller.mapper(instance.data.to_dict()),
                "fields": controller.fields,
            }
        )

    @route(r'/delete/{nested_pk:\w+}/', method='POST')
    async def post_delete(self, req: web.Request) -> None:
        pk = req.match_info['nested_pk']
        controller = self.get_controller()

        await controller.delete(int(pk))

        location = req.app.router[self.get_index_url_name()]\
            .url_for(pk=self.get_pk(req))\
            .with_query(f'message=The {self.get_name()}#{pk} has been deleted')

        raise web.HTTPFound(location=location)

    @route(r'/delete/{nested_pk:\w+}/', method='GET')
    async def get_delete(self, req: web.Request) -> web.Response:
        controller = self.get_controller()
        pk = self.get_pk(req)
        nested_pk = req.match_info['nested_pk']

        return aiohttp_jinja2.render_template(
            self.template_delete_name,
            req,
            {
                **await self.get_context(req),
                "title": (
                    f"Confirm delete {self.get_name()}#{nested_pk} relation"
                ),
                "controller": controller,
                "delete_url": (
                    req.app.router[self.get_url(self.post_delete).name]
                    .url_for(nested_pk=nested_pk, pk=pk)
                ),
                "pk": nested_pk,
            }
        )
