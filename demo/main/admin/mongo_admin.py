from aiohttp_admin2.controllers.mongo_controller import MongoController
from aiohttp_admin2.views import ControllerView
from umongo import Document, fields

from .injectors import instance


@instance.register
class User(Document):
    email = fields.EmailField(required=True, unique=True)

    class Meta:
        collection_name = "user"


class MongoTestController(MongoController, table=User):
    name = 'user mongo'
    per_page = 10


class MongoPage(ControllerView):
    controller = MongoTestController
