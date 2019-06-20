from .template_view import TemplateView

__all__ = ['DashboardView', ]


class DashboardView(TemplateView):
    """
    docs
    """
    template_name = 'admin/dashboard.html'
    index_url = '/'
    name = 'index'
    icon = 'dashboard'
    title = 'dashboard'
