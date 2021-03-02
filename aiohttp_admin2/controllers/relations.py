import typing as t
from dataclasses import dataclass


from aiohttp_admin2.view import ManyToManyTabView

if t.TYPE_CHECKING:
    from aiohttp_admin2.view import ControllerView


__all__ = ['ToManyRelation', 'ToOneRelation', ]


class ToManyRelation:
    """
    The current class need to describe one to many or many to many relation
    between two tables.
    """
    def __init__(
        self,
        name: str,
        left_table_pk: str,
        right_table_pk: str,
        relation_controller: t.Any,
    ) -> None:
        self.name = name
        self.left_table_pk = left_table_pk
        self.right_table_pk = right_table_pk
        self.relation_controller = relation_controller

    def accept(self, obj: 'ControllerView') -> None:
        tab = type(
            f'{self.__class__.__name__}ManyToManyTab',
            (ManyToManyTabView, ),
            {
                "name": self.name,
                "controller": self.relation_controller,
                "left_table_name": self.left_table_pk,
                "right_table_name": self.right_table_pk,
            }
        )

        obj.tabs.append(tab)


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
