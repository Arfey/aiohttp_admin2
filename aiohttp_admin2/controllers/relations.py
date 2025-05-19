import typing as t
from collections.abc import Callable
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from aiohttp_admin2.controllers.controller import Controller  # noqa
    from aiohttp_admin2.views import ControllerView  # noqa


__all__ = ['ToManyRelation', 'ToOneRelation', ]


@dataclass
class ToManyRelation:
    """
    The current class need to describe one to many or many to many relation
    between two tables.
    """
    name: str
    left_table_pk: str
    relation_controller: "Callable[..., Controller] | Controller"
    view_settings: dict[str, t.Any] | None = None

    def accept(self, obj: t.Type['ControllerView']) -> None:
        if callable(self.relation_controller):
            self.relation_controller = self.relation_controller()

        obj.visit_to_many_relations(self)


@dataclass
class ToOneRelation:
    """
    The current class need to describe one to one or many to one relation
    between two tables.
    """
    name: str
    field_name: str
    controller: t.Any
    hidden: bool = False
    target_field_name: str = None
