from umongo.document import MetaDocumentImplementation
from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.mappers.generics.mongo import MongoMapperGeneric
from aiohttp_admin2.resources.mongo_resource.mongo_resource import MongoResource  # noqa


__all__ = ["MongoController", ]


class MongoController(Controller):
    resource = MongoResource
    table: MetaDocumentImplementation

    def __init_subclass__(
        cls,
        table: MetaDocumentImplementation = None,
    ) -> None:
        # it only requires that the initialization of generic mappers and
        # controllers looks the same
        if table is not None and not getattr(cls, 'table', None):
            cls.table = table

        if not getattr(cls, 'mapper', None):
            class Mapper(MongoMapperGeneric, table=table):
                """
                If user don't specify mapper for controller we need to create
                it automatically
                """

            cls.mapper = Mapper

    def get_resource(self) -> MongoResource:
        return self.resource(self.table)
