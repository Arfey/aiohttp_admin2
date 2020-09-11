__all__ = ['BaseWidget', 'StringWidget']


class BaseWidget:
    template_name = 'aiohttp_admin/fields/string_field.html'


class StringWidget:
    template_name = 'aiohttp_admin/fields/string_field.html'


class ChoiceWidget:
    template_name = 'aiohttp_admin/fields/choice_field.html'
