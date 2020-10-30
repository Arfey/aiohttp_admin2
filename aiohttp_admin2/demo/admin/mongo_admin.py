from aiohttp_admin2.mappers.generics import MongoMapperGeneric
from aiohttp_admin2.controllers.mongo_controller import MongoController
from aiohttp_admin2.view import ControllerView
from umongo import Document, fields

from .injectors import instance


@instance.register
class User(Document):
    email = fields.EmailField(required=True, unique=True)

    class Meta:
        collection_name = "user"


class MongoTestMapper(MongoMapperGeneric, table=User):
    pass


class MongoTestController(MongoController):
    mapper = MongoTestMapper
    table = User
    name = 'user_mongo'
    per_page = 10


class MongoPage(ControllerView):
    controller = MongoTestController
