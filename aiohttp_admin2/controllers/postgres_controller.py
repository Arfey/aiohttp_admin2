import sqlalchemy as sa

from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.resources.postgres_resource.postgres_resource import \
    PostgresResource
from aiohttp_admin2.connection_injectors import ConnectionInjector
from aiohttp_admin2.mappers import (
    fields,
    Mapper,
)


__all__ = ["PostgresController", "ManyToManyPostgresController", ]


class PostgresController(Controller):
    table: sa.Table
    resource = PostgresResource
    connection_injector: ConnectionInjector

    def get_resource(self) -> PostgresResource:
        return self.resource(
            self.connection_injector.connection,
            self.table,
            custom_sort_list={
                key.replace('_field_sort', ''): getattr(self, key)
                for key in dir(self)
                if key.endswith('_field_sort')
            },
        )


class ManyToManyPostgresController(PostgresController):
    per_page = 1000
    table: sa.Table
    target_table: sa.Table

    left_table_name: str
    right_table_name: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mapper = type(
            f"{self.__class__.__name__}Mapper",
            (Mapper, ),
            {
                str(self.left_table_name): fields.IntField(required=True),
                str(self.right_table_name): fields.IntField(required=True)
            },
        )
