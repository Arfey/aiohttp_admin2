from .template_view import TemplateView

__all__ = ['DashboardView', ]


class DashboardView(TemplateView):
    """
    docs
    """
    template_name = 'admin/index.html'
    url = '/'
    name = 'index'
