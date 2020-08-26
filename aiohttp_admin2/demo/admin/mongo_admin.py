from aiohttp_admin2.mappers.generics import MongoMapperGeneric
from aiohttp_admin2.controllers.mongo_controller import MongoController
from aiohttp_admin2.view import ControllerView

from ..catalog.mongo_table import TestTable


class MongoTestMapper(MongoMapperGeneric, table=TestTable):
    pass


class MongoTestController(MongoController):
    pass


class MongoControllerView(ControllerView):
    controller = MongoTestController


# todo: added some like MotorAsyncIOInstance for db https://github.com/sneawo/asyncio-rest-example/blob/master/app/db.py
