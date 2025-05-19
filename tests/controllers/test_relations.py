from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.controllers.relations import ToManyRelation
from aiohttp_admin2.views import ControllerView


class MockController(Controller):
    pass


class TestToManyRelation:
    def test_success_creation(self):
        relation = ToManyRelation(
            name="name",
            left_table_pk="id",
            relation_controller=MockController,
        )

        assert relation.name == "name"
        assert relation.left_table_pk == "id"
        assert relation.view_settings is None

        relation = ToManyRelation(
            name="name",
            left_table_pk="id",
            view_settings={"key": "value"},
            relation_controller=MockController,
        )

        assert relation.name == "name"
        assert relation.left_table_pk == "id"
        assert relation.view_settings == {"key": "value"}

    def test_accept_with_view_settings(self):
        class MockControllerView(ControllerView):
            _tabs = []

        relation1 = ToManyRelation(
            name="name1",
            left_table_pk="id",
            view_settings={"infinite_scroll": True},
            relation_controller=MockController,
        )
        relation2 = ToManyRelation(
            name="name2",
            left_table_pk="id",
            relation_controller=MockController,
        )

        relation1.accept(MockControllerView)
        relation2.accept(MockControllerView)

        assert len(MockControllerView._tabs) == 2
        assert MockControllerView._tabs[0].infinite_scroll == True
        assert MockControllerView._tabs[1].infinite_scroll == False
