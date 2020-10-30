from aiohttp_admin2.view.aiohttp.views.template_view import TemplateView
from aiohttp_admin2.view.aiohttp.views.base import BaseAdminView
from aiohttp_admin2.view.aiohttp.views.dashboard import DashboardView
from aiohttp_admin2.view.aiohttp.views.controller_view import ControllerView
from aiohttp_admin2.view.aiohttp.views.tab_template_view import TabTemplateView
from aiohttp_admin2.view.aiohttp.views.many_to_many_tab_view import \
    ManyToManyTabView
from aiohttp_admin2.view.aiohttp.admin import Admin


__all__ = [
    'TemplateView',
    'DashboardView',
    'Admin',
    'BaseAdminView',
    'ControllerView',
    'TabTemplateView',
    'ManyToManyTabView',
]
