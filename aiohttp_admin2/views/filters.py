import typing as t
from abc import ABC
from abc import abstractmethod

from aiohttp_admin2.mappers.fields.abc import AbstractField
from aiohttp_admin2.resources.types import FilterTuple
from aiohttp_admin2.resources.types import FilterMultiTuple


class FilerBase(ABC):
    template_name: str
    name: str
    query: dict
    field: AbstractField

    js_extra: t.List[str] = []
    css_extra: t.List[str] = []

    @abstractmethod
    def get_filter_list(self): pass


class ChoiceFilter(FilerBase):
    template_name = 'aiohttp_admin/blocks/filters/choice_filter.html'
    name: str
    query: dict
    field: AbstractField

    def __init__(self, field: AbstractField, query: dict) -> None:
        self.field = field
        self.name = field.name
        self.query = query
        self.param_key = f'choice_{field.name}'

    def get_param(self):
        return self.query.get(self.param_key)

    def get_filter_list(self):
        param = self.get_param()

        if param:
            return [FilterTuple(self.name, param, 'eq')]

        return []


class BooleanFilter(FilerBase):
    template_name = 'aiohttp_admin/blocks/filters/boolean_filter.html'
    name: str
    query: dict
    field: AbstractField

    def __init__(self, field: AbstractField, query: dict) -> None:
        self.field = field
        self.name = field.name
        self.query = query
        self.param_key = f'bool_{self.name}'

    def get_param(self):
        return self.query.get(self.param_key)

    def get_filter_list(self):
        param = self.get_param()

        if param:
            return [FilterTuple(self.name, param, 'eq')]

        return []


class SingleValueFilter(FilerBase):
    template_name = 'aiohttp_admin/blocks/filters/single_value_filter.html'
    name: str
    query: dict
    field: AbstractField

    def __init__(self, field: AbstractField, query: dict) -> None:
        self.field = field
        self.name = field.name
        self.query = query
        self.param_key = f'single_value_{self.name}'

    def get_param(self):
        return self.query.get(self.param_key)

    def get_filter_list(self):
        param = self.get_param()

        if param:
            return [FilterTuple(self.name, param, 'eq')]

        return []


class DateTimeFilter(FilerBase):
    template_name = 'aiohttp_admin/blocks/filters/datetime_filter.html'
    name: str
    query: dict
    field: AbstractField
    format: str = 'YYYY-MM-DD HH:mm:ss'

    js_extra = [
        "https://code.jquery.com/jquery-3.5.1.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.22.2/moment.min.js",  # noqa
        "https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/5.0.1/js/tempusdominus-bootstrap-4.min.js"  # noqa

    ]
    css_extra = [
        "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css",  # noqa
        "https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/5.0.1/css/tempusdominus-bootstrap-4.min.css",  # noqa
    ]

    def __init__(self, field: AbstractField, query: dict) -> None:
        self.field = field
        self.name = field.name
        self.query = query
        self.param_key_from = f'date_from_{self.name}'
        self.param_key_to = f'date_to__{self.name}'

    def get_params(self):
        return (
            self.query.get(self.param_key_from),
            self.query.get(self.param_key_to)
        )

    def get_filter_list(self):
        params = self.get_params()

        filters = []

        if params[0]:
            return [FilterTuple(self.name, params[0], 'gte')]

        if params[1]:
            return [FilterTuple(self.name, params[1], 'lte')]

        return filters


class DateFilter(DateTimeFilter):
    format: str = 'YYYY-MM-DD'


class SearchFilter(FilerBase):
    template_name = 'aiohttp_admin/blocks/filters/search_filter.html'
    name: str
    query: dict
    fields: t.List[str]

    def __init__(self, fields: t.List[str], query) -> None:
        self.fields = fields
        self.name = 'search'
        self.param_key = self.name
        self.query = query

    def get_param(self):
        return self.query.get(self.param_key)

    def get_filter_list(self):
        param = self.get_param()

        if param:
            return [FilterMultiTuple(self.fields, param, 'search_multi')]

        return []
