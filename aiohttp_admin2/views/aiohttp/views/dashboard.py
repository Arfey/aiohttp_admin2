from aiohttp_admin2.views import TemplateView


__all__ = ['DashboardView', ]


class DashboardView(TemplateView):
    """
    This class need for represent a main page for admin interface.
    """
    index_url = '/'
    name = 'index'
    icon = 'dashboard'

    @classmethod
    def get_index_url(cls):
        return cls.index_url
