from aiohttp_admin2.resources.mysql_resource.mysql_resource import MySqlResource  # noqa
from aiohttp_admin2.controllers.postgres_controller import PostgresController

__all__ = ["MySQLController", ]


class MySQLController(PostgresController):
    resource = MySqlResource

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
