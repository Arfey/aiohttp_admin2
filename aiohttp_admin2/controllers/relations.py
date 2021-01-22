import typing as t

from aiohttp_admin2.view import ManyToManyTabView

if t.TYPE_CHECKING:
    from aiohttp_admin2.view import ControllerView


__all__ = ['CrossTableRelation', ]


class CrossTableRelation:
    """
    Current class need to describe relation between to tables which implement
    via other table (many to many).
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
