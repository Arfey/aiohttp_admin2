from umongo.document import MetaDocumentImplementation
from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.resources.mongo_resource.mongo_resource import \
    MongoResource


__all__ = ["MongoController", ]


class MongoController(Controller):
    resource = MongoResource
    table: MetaDocumentImplementation

    def get_resource(self) -> MongoResource:
        return self.resource(self.table)
