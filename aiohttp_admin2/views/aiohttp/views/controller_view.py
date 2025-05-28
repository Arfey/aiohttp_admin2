import typing as t

import aiohttp_jinja2
from aiohttp import web

from aiohttp_admin2.views.aiohttp.views.base import BaseControllerView
from aiohttp_admin2.views.aiohttp.views.many_to_many_tab_view import ManyToManyTabView  # noqa
from aiohttp_admin2.controllers.relations import ToManyRelation
from aiohttp_admin2.resources.types import Instance
from aiohttp_admin2.controllers.controller import DETAIL_NAME
from aiohttp_admin2.controllers.controller import FOREIGNKEY_DETAIL_NAME
from aiohttp_admin2.views.aiohttp.views.utils import route
from aiohttp_admin2.mappers import Mapper
from aiohttp_admin2.views.aiohttp.views.base import global_views_instance

__all__ = ['ControllerView', ]


class ControllerView(BaseControllerView):
    """
    This class need for represent a pages based on controller for admin
    interface.
    """

    @classmethod
    def get_index_url_name(cls):
        return cls.controller.url_name()

    @classmethod
    def get_index_url(cls):
        return str(cls.index_url or f'/{cls.get_index_url_name()}/')

    def get_detail_url(self):
        return self.get_url(self.get_detail).name

    @classmethod
    def get_name(cls):
        """This method return the pretty name of the current views"""
        return str(cls.name or cls.controller.get_name())

    def tabs_list(self):
        views = global_views_instance.get() or []
        return [
            v for v in views
            if v.__class__ in self._tabs and v.get_controller().can_view
        ]

    @route(r'/')
    async def get_list(self, req: web.Request) -> web.Response:
        params = self.get_params_from_request(req)
        controller = self.get_controller()

        filters = self.get_list_filters(
            req,
            controller,
            self.default_filter_map,
        )

        url_name_maps = {
            i.get_controller().url_name(): i.get_detail_url()
            for i in global_views_instance.get() or []
            if hasattr(i, 'controller')
        }

        def url_builder(obj: Instance, url_type: str, **kwargs) -> str:
            if url_type is DETAIL_NAME:
                return str(
                    req.app.router[self.get_url(self.get_detail).name]
                    .url_for(pk=str(obj.get_pk()))
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
            filters=filters,
            url_builder=url_builder,
            with_count=not self.infinite_scroll,
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
                "create_url": str(
                    req.app.router[self.get_url(self.get_create).name]
                    .url_for()
                ),
                "media": self.get_extra_media_list(),
                "view_filters": self.get_filters(req.rel_url.query),
            }
        )

    @route(r'/{pk:\w+}/')
    async def get_detail(
        self,
        req: web.Request,
        mapper: t.Dict[str, t.Any] = None,
    ) -> web.Response:
        controller = self.get_controller()
        # todo: handle str key for dict
        pk = req.match_info['pk']
        instance = await controller.get_detail(pk)

        template = self.template_detail_edit_name

        if not controller.can_update:
            template = self.template_detail_name

        return aiohttp_jinja2.render_template(
            template,
            req,
            {
                **await self.get_context(req),
                "media": self.get_extra_media(),
                "object": instance,
                "controller": controller,
                "title": f"{self.get_name()}#{pk}",
                "delete_url": (
                    req.app.router[self.get_url(self.get_delete).name]
                    .url_for(pk=pk)
                ),
                "detail_url": (
                    req.app.router[self.get_url(self.get_detail).name]
                    .url_for(pk=pk)
                ),
                "save_url": (
                    req.app.router[self.get_url(self.post_update).name]
                    .url_for(pk=pk)
                ),
                "mapper": mapper or controller.mapper(instance.data.to_dict()),
                "fields": controller.fields,
                "exclude_fields": self.controller.exclude_update_fields,
                "read_only_fields": self.controller.read_only_fields,
                "is_common": True,
                "tabs": self.tabs_list(),
                "pk": pk,
            }
        )

    @route(r'/create/')
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
                "title": f"Create a new {self.get_name()}",
                "mapper": mapper or controller.mapper({}),
                "fields": controller.fields,
                "exclude_fields": self.controller.exclude_create_fields,
                "read_only_fields": self.controller.read_only_fields,
                "create_post_url": str(
                    req.app.router[self.get_url(self.post_create).name]
                    .url_for()
                ),
            }
        )

    @route(r'/create/', method='POST')
    async def post_create(self, req: web.Request) -> web.Response:
        controller = self.get_controller()
        data = dict(await req.post())

        obj = await controller.create(data)

        if isinstance(obj, Mapper):
            return await self.get_create(req, obj)
        else:
            raise web.HTTPFound(
                req.app.router[self.get_url(self.get_detail).name]
                .url_for(pk=str(obj.get_pk()))
                .with_query(
                    f'message=The {self.get_name()}#{obj.get_pk()} '
                    f'has been created'
                )
            )

    # todo: concat post and get update
    @route(r'/{pk:\w+}/', method="POST")
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
                req.app.router[self.get_url(self.get_detail).name]
                .url_for(pk=pk)
                .with_query(
                    f'message=The {self.get_name()}#{pk} has been updated'
                )
            )

    @route(r'/{pk:\w+}/delete/')
    async def get_delete(self, req: web.Request) -> web.Response:
        pk = req.match_info['pk']
        controller = self.get_controller()

        return aiohttp_jinja2.render_template(
            self.template_delete_name,
            req,
            {
                **await self.get_context(req),
                "title": f"Confirm delete {self.get_name()}#{pk}",
                "controller": controller,
                "delete_url": (
                    req.app.router[self.get_url(self.post_delete).name]
                    .url_for(pk=pk)
                ),
                "pk": pk,
            }
        )

    @route(r'/{pk:\w+}/delete/', method="POST")
    async def post_delete(self, req: web.Request) -> None:
        controller = self.get_controller()
        pk = req.match_info['pk']
        await controller.delete(int(pk))
        location = req.app.router[self.get_index_url_name()]\
            .url_for()\
            .with_query(f'message=The {self.get_name()}#{pk} has been deleted')
        raise web.HTTPFound(location=location)

    @classmethod
    def visit_to_many_relations(cls, obj: ToManyRelation) -> None:
        kwargs = {
            "name": obj.name,
            "controller": obj.relation_controller,
            "left_table_pk_name": obj.left_table_pk,
        }
        tab_name = f'{cls.__name__}AutogenerateManyToManyTab'

        if obj.view_settings:
            kwargs.update(obj.view_settings)

        cls.add_tab(type(tab_name, (ManyToManyTabView,), kwargs))
