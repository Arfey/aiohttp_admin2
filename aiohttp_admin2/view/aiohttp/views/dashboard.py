from aiohttp_admin2.view import TemplateView


__all__ = ['DashboardView', ]

#todo: add docs
class DashboardView(TemplateView):
    """
    This class need for represent a main page for admin interface.
    """
    index_url = '/'
    name = 'index'
    controller_url = 'index'
    icon = 'dashboard'
    title = 'dashboard'
