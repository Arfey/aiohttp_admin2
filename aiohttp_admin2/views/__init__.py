from aiohttp_admin2.views.aiohttp.views.template_view import TemplateView
from aiohttp_admin2.views.aiohttp.views.base import BaseAdminView
from aiohttp_admin2.views.aiohttp.views.dashboard import DashboardView
from aiohttp_admin2.views.aiohttp.views.controller_view import ControllerView
from aiohttp_admin2.views.aiohttp.views.tab_template_view import TabTemplateView   # noqa
from aiohttp_admin2.views.aiohttp.views.many_to_many_tab_view import ManyToManyTabView  # noqa
from aiohttp_admin2.views.aiohttp.admin import Admin


__all__ = [
    'TemplateView',
    'DashboardView',
    'Admin',
    'BaseAdminView',
    'ControllerView',
    'TabTemplateView',
    'ManyToManyTabView',
]
