import sqlalchemy as sa

from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.resources.mysql_resource.mysql_resource import MySqlResource  # noqa
from aiohttp_admin2.connection_injectors import ConnectionInjector


__all__ = ["MySQLController", ]


class MySQLController(Controller):
    table: sa.Table
    resource = MySqlResource
    connection_injector: ConnectionInjector

    def get_resource(self) -> MySqlResource:
        return self.resource(
            self.connection_injector.connection,
            self.table,
            custom_sort_list={
                key.replace('_field_sort', ''): getattr(self, key)
                for key in dir(self)
                if key.endswith('_field_sort')
            },
        )
