from aiohttp_admin2.resources.types import FilterTuple


class ChoiceFilter:
    template_name = 'aiohttp_admin/filters/choice_filter.html'
    name: str
    query: dict

    def __init__(self, name: str, query: dict) -> None:
        self.name = name
        self.query = query
        self.params_key = [f'{name}']

    def get_param(self):
        return self.query.get(f'{self.name}')

    def get_filter_list(self):
        param = self.get_param()

        if param:
            return [FilterTuple(self.name, param, 'eq')]

        return []
