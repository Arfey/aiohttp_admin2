from .template_view import TemplateView

__all__ = ['DashboardView', ]


class DashboardView(TemplateView):
    """
    This class created for representation index page of the admin.
    """
    index_url = '/'
    name = 'index'
    icon = 'dashboard'
    title = 'dashboard'
