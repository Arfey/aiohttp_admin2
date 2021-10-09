import typing as t
from contextvars import ContextVar
from collections import defaultdict

from aiohttp import web
from aiohttp_admin2.views.aiohttp.views.utils import get_route
from aiohttp_admin2.views.aiohttp.views.utils import UrlInfo
from aiohttp_admin2.views.aiohttp.views.utils import IsNotRouteAdminException
from aiohttp_admin2.views.aiohttp.views.utils import get_list_filters
from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.views import widgets
from aiohttp_admin2.views import filters
from aiohttp_admin2.views.filters import FilerBase
from aiohttp_admin2.mappers import fields
from aiohttp_admin2.views.aiohttp.utils import get_params_from_request
from aiohttp_admin2.views.aiohttp.utils import QueryParams
from aiohttp_admin2.resources.types import FilterTuple
from aiohttp_admin2.views.aiohttp.exceptions import CanNotModifiedFrozenView
from aiohttp_admin2.views.aiohttp.exceptions import CanNotCreateUnfrozenView
from aiohttp_admin2.views.aiohttp.exceptions import UseHandlerWithoutAccess
from aiohttp_admin2.views.aiohttp.exceptions import NotRegisterView
from aiohttp_admin2.controllers.controller import controllers_map
from aiohttp_admin2.controllers.exceptions import PermissionDenied

if t.TYPE_CHECKING:
    from aiohttp_admin2.views.aiohttp.views.tab_base_view import TabBaseView # noqa

__all__ = [
    'BaseAdminView',
    'BaseControllerView',
    'global_list_view',
    'global_views_instance',
]


DEFAULT_TYPE_WIDGETS = {
    fields.StringField.type_name: widgets.StringWidget,
    fields.LongStringField.type_name: widgets.LongStringWidget,
    fields.ChoicesField.type_name: widgets.ChoiceWidget,
    fields.BooleanField.type_name: widgets.BooleanWidget,
    fields.ArrayField.type_name: widgets.ArrayWidget,
    fields.DateTimeField.type_name: widgets.DateTimeWidget,
    fields.DateField.type_name: widgets.DateWidget,
    fields.JsonField.type_name: widgets.JsonWidget,
    fields.UrlFileField.type_name: widgets.FileWidget,
    fields.UrlImageField.type_name: widgets.ImageWidget,
    'autocomplete': widgets.AutocompleteStringWidget,
}

DEFAULT_FILTER_MAP = {
    fields.ChoicesField.type_name: filters.ChoiceFilter,
    fields.BooleanField.type_name: filters.BooleanFilter,
    fields.DateTimeField.type_name: filters.DateTimeFilter,
    fields.DateField.type_name: filters.DateFilter,
    fields.StringField.type_name: filters.SingleValueFilter,
    fields.UrlFileField.type_name: filters.SingleValueFilter,
    fields.UrlImageField.type_name: filters.SingleValueFilter,
    fields.IntField.type_name: filters.SingleValueFilter,
}

# this context map to share list of all views which added to the admin
# interface
ViewsMap = ContextVar[t.List[t.Type['BaseAdminView']]]
global_list_view: ViewsMap = ContextVar('global_list_view', default=None)

ViewsInstanceMap = ContextVar[t.List['BaseAdminView']]
global_views_instance: ViewsInstanceMap = ContextVar(
    'views_instance_map',
    default=None,
)


class BaseAdminView:
    """
    The base class for views in admin interface. The each views must inherit
    from it.
    """

    def __init__(self, request, *args, **kwargs):
        self.request = request

    # True if the views is frozen and we can't modified static properties
    _is_frozen: bool = False

    @classmethod
    def _raise_if_frozen(cls):
        if cls._is_frozen:
            raise CanNotModifiedFrozenView

    @classmethod
    def _raise_if_unfrozen(cls):
        if not cls._is_frozen:
            raise CanNotCreateUnfrozenView(
                "U need setup views before instantiate it."
            )

    # True if the access hook have been call
    _is_checked_access: bool = False

    def _raise_if_no_checked_access(self):
        if not self._is_checked_access:
            raise UseHandlerWithoutAccess

    # List of tabs for current views
    _tabs: t.List[t.Type['TabBaseView']] = None

    @classmethod
    def add_tab(cls, tab: t.Type['TabBaseView']) -> None:
        cls._raise_if_frozen()
        cls._tabs.append(tab)

    # The url prefix path for all routes related with the current views.
    index_url: str = None

    @classmethod
    def get_index_url(cls):
        """
        This method return the url of the index page of the current views.
        """
        return str(cls.index_url or f'/{cls.__name__.lower()}/')

    @classmethod
    def get_index_url_name(cls):
        """This method return the name of the index url route."""

        name = cls.name or cls.__name__.lower()

        return "_".join(name.split(" "))

    # This string will use as the pretty name of the current views in the
    # admin interface.
    name: str = None

    @classmethod
    def get_name(cls):
        """This method return the pretty name of the current views."""
        return str(cls.name or f'{cls.__name__.lower()}')

    # This string set a type of icon which will use in aside bar for the
    # current views
    icon: str = 'label'

    # If views have the same group name then they will organize together into
    # separate block in the aside bar
    group_name: str = 'General'

    # if we don't want to show link on current views in the aside bar then we
    # need to set True
    is_hide_view: bool = False

    # Set to True if we don't want to give access to current views
    has_access: bool = True

    def get_nav_groups(self) -> t.Dict[str, t.List[t.Type['BaseAdminView']]]:
        nav_groups = defaultdict(list)
        views = global_views_instance.get() or []

        for view in views:
            if not view.is_hide_view and view.has_access:
                nav_groups[view.group_name].append(view)

        return nav_groups

    async def get_context(self, req: web.Request) -> t.Dict[str, t.Any]:
        """
        In this place you can redefine whole context which will use for
        generate custom page.
        """
        return {
            "request": req,
            "title": self.get_name(),
            "controller_view": self,
            "url_query": req.rel_url.query,
            "url_path": req.rel_url.path,
            "message": req.rel_url.query.get('message'),
            "nav_groups": self.get_nav_groups(),
        }

    @classmethod
    def get_tabs(cls):
        cls._raise_if_unfrozen()
        return cls._tabs

    @classmethod
    def setup(
        cls,
        app: web.Application,
    ) -> None:
        """
        This method have to initialize routes related with current views. On
        each request must create new views instance.
        """
        cls._raise_if_frozen()
        cls._tabs = cls._tabs or []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            route_info = get_route(attr)
            if route_info:
                url_info = cls.get_url(attr)

                app.add_routes([
                    web.route(
                        method=route_info.method,
                        path=url_info.url,
                        handler=cls._handler_builder(attr),
                        name=url_info.name
                    )
                ])

        if hasattr(cls, 'controller'):
            for relation in cls.controller.relations_to_many:
                relation.accept(cls)

        # setup tabs views
        for tab in cls._tabs:
            tab.set_parent(cls)

        for tab in cls._tabs:
            tab.setup(app)
            views = global_views_instance.get() or []
            global_views_instance.set([*views, tab])

        cls._is_frozen = True

    @classmethod
    def get_url(cls, handler) -> UrlInfo:
        """
        The current method return url info for received handler.
        """
        route_info = get_route(handler)

        if not route_info:
            raise IsNotRouteAdminException(
                f'{handler} don`t have route info. Try to wrap this handler'
                f'via @route decorator'
            )

        if route_info.url == '/':
            name = cls.get_index_url_name()
        else:
            name = cls.get_index_url_name() + '_' + handler.__name__

        return UrlInfo(
            url=(cls.get_index_url() + route_info.url[1:]),
            name=name,
        )

    @classmethod
    def _handler_builder(cls, fn):
        """
        The each request have to generate new views for correction work of
        permission access and the current method implement this requirement.
        """
        async def handler(request: web.Request) -> web.Response:
            cls._raise_if_unfrozen()
            controllers_map.set({})
            views = global_list_view.get() or []
            views_instance = []
            current_view = None

            for view in views:
                view_instance = view(request)
                await view_instance._inner_access_hook()
                views_instance.append(view_instance)

                if view is cls:
                    current_view = view_instance

            if not current_view:
                raise NotRegisterView

            current_view._raise_if_no_checked_access()

            global_views_instance.set(views_instance)

            if not current_view.has_access:
                raise PermissionDenied

            return await getattr(current_view, fn.__name__)(request)

        return handler

    async def access_hook(self) -> None:
        """
        This method need to redefine settings for each request.
        """

    async def _inner_access_hook(self) -> None:
        self._is_checked_access = True
        await self.access_hook()


class BaseControllerView(BaseAdminView):
    # Templates
    template_list_name = 'aiohttp_admin/layouts/list_page.html'
    template_list_cursor_name = 'aiohttp_admin/layouts/list_cursor_page.html'
    template_detail_name = 'aiohttp_admin/layouts/detail_view_page.html'
    template_detail_edit_name = 'aiohttp_admin/layouts/detail_edit_page.html'
    template_detail_create_name = 'aiohttp_admin/layouts/create_page.html'
    template_delete_name = 'aiohttp_admin/layouts/delete_page.html'

    infinite_scroll = False
    fields_widgets = {}
    default_widget = widgets.StringWidget
    foreignkey_widget = widgets.AutocompleteStringWidget
    type_widgets = {}
    common_type_widgets = {}
    default_type_widgets = DEFAULT_TYPE_WIDGETS
    default_filter_map = DEFAULT_FILTER_MAP
    search_filter = filters.SearchFilter

    controller: t.Type[Controller]
    _controller: Controller

    def __init__(
        self,
        request=None,
        params: t.Dict[str, t.Any] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(request, *args, **kwargs)
        self._controller = self.controller.builder()
        self.params = params or {}
        # todo: setup before create error

        # todo: move to base and fix super
        self.common_type_widgets = {
            **self.default_type_widgets,
            **self.type_widgets
        }

    @staticmethod
    def get_params_from_request(req: web.Request) -> QueryParams:
        return get_params_from_request(req)

    def get_widget_template_for_field(
        self,
        name: str,
        field_type: str,
    ) -> str:
        foreign_key_controller = self\
            .get_controller()\
            .foreign_keys_field_map.get(name)

        if (
            foreign_key_controller
            and foreign_key_controller.controller.with_autocomplete()
        ):
            widget = self.foreignkey_widget
        else:
            widget = self.fields_widgets.get(name)

            if not widget:
                widget = self.common_type_widgets\
                    .get(field_type, self.default_widget)

        return widget.template_name

    def get_filters(self, query) -> t.List[t.Tuple[str, FilerBase]]:
        controller = self.get_controller()
        empty_mapper = controller.mapper({})

        filters = []

        for f in controller.list_filter:
            field = empty_mapper._fields.get(f)
            filter_cls = self.default_filter_map.get(field.type_name)

            if filter_cls:
                filters.append((f, filter_cls(field, query)))
        return filters

    @staticmethod
    def get_list_filters(
            req: web.Request,
            controller: Controller,
            filter_mapper: t.Dict[str, t.Any],
    ) -> t.List[t.Union[FilerBase, FilterTuple]]:
        """
        In this method we extract filter from request params and return
        represented as list of internal classes.
        """
        return get_list_filters(req, controller, filter_mapper)

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

    @classmethod
    def get_autocomplete_url(cls, name: str) -> str:
        return f'/{cls.get_index_url_name()}/_autocomplete_{name}'

    @classmethod
    def get_autocomplete_url_name(cls, name: str) -> str:
        return f'{cls.get_index_url_name()}_autocomplete_{name}'

    def get_controller(self) -> Controller:
        return self._controller

    @classmethod
    def setup(
        cls,
        app: web.Application,
    ) -> None:
        super().setup(app)
        controller = cls.controller.builder()

        # autocomplete
        autocomplete_routes = []
        for name, relation in controller.foreign_keys_field_map.items():
            def autocomplete_wrapper(inner_controller):
                async def autocomplete(req):
                    res = await inner_controller\
                        .get_autocomplete_items(
                            text=req.rel_url.query.get('q'),
                            page=int(req.rel_url.query.get('page', 1)),
                        )

                    return web.json_response(res)

                return autocomplete

            autocomplete_routes.append(web.get(
                cls.get_autocomplete_url(name),
                autocomplete_wrapper(relation.controller.builder()),
                name=cls.get_autocomplete_url_name(name)
            ))

        app.add_routes(autocomplete_routes)

    async def _inner_access_hook(self) -> None:
        await super()._inner_access_hook()

        if not self.is_hide_view:
            self.is_hide_view = not self.get_controller().can_view
