from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.mappers import (
    Mapper,
    fields,
)
from aiohttp_admin2.resources.dict_resource.dict_resource import DictResource


class MockMapper(Mapper):
    id = fields.StringField(required=True)


class MockController(Controller):
    mapper = MockMapper
    resource = DictResource

    def get_resource(self) -> DictResource:
        return DictResource({i: {"id": i} for i in range(20)})


async def test_get_list_without_count():
    list_objects = await MockController().get_list(
        url_builder=lambda *args: "", with_count=True
    )
    assert list_objects.count == 20

    list_objects = await MockController().get_list(
        url_builder=lambda *args: "", with_count=False
    )
    assert list_objects.count is None
