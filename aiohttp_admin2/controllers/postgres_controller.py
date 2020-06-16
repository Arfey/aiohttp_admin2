import typing as t

import sqlalchemy as sa
from aiopg.sa import Engine

from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.resources.postgres_resource.postgres_resource import \
    PostgresResource


__all__ = ["PostgresController", ]


class PostgresController(Controller):
    table: sa.Table
    resource = PostgresResource
    engine: Engine
    engine_name: str = ''

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    @classmethod
    def builder_form_params(cls, params: t.Dict[str, t.Any]):
        engine = params.get("engines", {}).get(cls.engine_name)
        return cls(engine)

    def get_resource(self):
        return self.resource(self.engine, self.table)
