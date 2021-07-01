import sqlalchemy as sa

from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.resources.postgres_resource.postgres_resource import PostgresResource  # noqa
from aiohttp_admin2.connection_injectors import ConnectionInjector


__all__ = ["PostgresController", ]


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
