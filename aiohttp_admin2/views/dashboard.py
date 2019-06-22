from .template_view import TemplateAdminView

__all__ = ['DashboardView', ]


class DashboardView(TemplateAdminView):
    """
    This class created for representation index page of the admin.
    """
    index_url = '/'
    name = 'index'
    icon = 'dashboard'
    title = 'dashboard'
