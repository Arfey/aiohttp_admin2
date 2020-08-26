import typing as t

from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.resources.mongo_resource.mongo_resource import \
    MongoResource


__all__ = ["MongoController", ]


class MongoController(Controller):
    table: sa.Table
    resource = MongoResource

    def get_resource(self) -> MongoResource:
        return self.resource(self.table)
