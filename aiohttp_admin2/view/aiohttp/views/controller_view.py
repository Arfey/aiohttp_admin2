from aiohttp import web
import aiohttp_jinja2
import typing as t

from aiohttp_admin2.view.aiohttp.views.base import BaseAdminView
from aiohttp_admin2.view.aiohttp.views.tab_base_view import TabBaseView
from aiohttp_admin2.controllers.controller import Controller


class ControllerView(BaseAdminView):
    """
    This class need for represent a pages based on controller for admin
    interface.
    """
    # Templates
    template_list_name = 'aiohttp_admin/list.html'
    template_detail_name = 'aiohttp_admin/detail.html'
    template_detail_edit_name = 'aiohttp_admin/detail_edit.html'
    template_detail_create_name = 'aiohttp_admin/create.html'
    template_delete_name = 'aiohttp_admin/delete.html'
    controller: Controller
    tabs: t.List[TabBaseView] = None
    tabs_list: t.List[t.Any] = None
    relations: t.List[t.Any] = []

    # Fields
    exclude_fields = ['id', ]

    def __init__(self, *, params: t.Dict[str, t.Any] = None) -> None:
        self.tabs_list = self.tabs_list or []
        self.tabs = self.tabs or []
        default = self.controller.name

        self.controller_url = self.controller.url_name()
        self.index_url = self.index_url or f'/{self.controller_url}/'
        self.name = self.name or default

        self.title = self.title if not self.title == 'None' else default
        self.params = params or {}

        for relation in self.relations:
            relation.accept(self)

        if self.tabs:
            self.tabs_list = [Tab(self) for Tab in self.tabs]

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

    @property
    def index_url_name(self):
        return self.controller_url

    def get_controller(self):
        return self.controller.builder_form_params(self.params)

    async def get_list(self, req: web.Request) -> web.Response:
        params = self.get_params_from_request(req)
        controller = self.get_controller()

        filters = self.get_list_filters(
            req,
            controller,
            self.default_filter_map,
        )

        data = await controller.get_list(**params._asdict(), filters=filters)

        # list_filter
        return aiohttp_jinja2.render_template(
            self.template_list_name,
            req,
            {
                **await self.get_context(req),
                "list": data,
                "controller": controller,
                "detail_url": self.detail_url_name,
                "create_url": self.create_url_name,
                "message": req.rel_url.query.get('message'),
                "media": self.get_extra_media_list(),
            }
        )

    async def get_detail(
        self,
        req: web.Request,
        mapper: t.Dict[str, t.Any] = None,
    ) -> web.Response:
        controller = self.get_controller()
        # todo: handle str key for dict
        data = await controller.get_detail(req.match_info['pk'])

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
                "delete_url": self.delete_url_name,
                "detail_url": self.detail_url_name,
                "save_url": self.update_post_url_name,
                "mapper": mapper or controller.mapper(data.__dict__),
                "fields": controller.fields,
                "message": req.rel_url.query.get('message'),
                "exclude_fields": self.exclude_fields,
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
                "create_url": self.create_post_url_name,
                "mapper": mapper or controller.mapper({}),
                "fields": controller.fields,
                "exclude_fields": self.exclude_fields,
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
                req.app.router[self.detail_url_name]
                    .url_for(pk=str(obj.id))
                    .with_query(
                        f'message=The {self.name}#{obj.id} has been created'
                    )
            )
        else:
            return await self.get_create(req, mapper)

    # todo: concat post and get update
    async def post_update(self, req: web.Request) -> web.Response:
        controller = self.get_controller()
        data = dict(await req.post())
        # todo: get_pk_name
        pk = req.match_info['pk']
        data['id'] = pk

        mapper = controller.mapper(dict(data))

        if mapper.is_valid():
            serialize_data = mapper.data
            del serialize_data['id']
            await controller.update(pk, serialize_data)

            raise web.HTTPFound(
                req.app.router[self.detail_url_name]
                    .url_for(pk=pk)
                    .with_query(
                        f'message=The {self.name}#{pk} has been updated'
                    )
            )
        else:
            return await self.get_detail(req, mapper)

    async def get_delete(self, req: web.Request) -> web.Response:
        return aiohttp_jinja2.render_template(
            self.template_delete_name,
            req,
            {
                **await self.get_context(req),
                "title": f"Confirm delete {self.name}#{req.match_info['pk']}",
                "delete_url": self.delete_post_url_name,
                "pk": req.match_info['pk'],
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
