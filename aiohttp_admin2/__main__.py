import asyncio
from aiopg.sa import create_engine
import sqlalchemy as sa
from aiohttp_admin2.resources import PostgresResource
from aiohttp_admin2.resources import MongoResource
from aiohttp_admin2.resources import Instance
from aiohttp_admin2.resources.types import FilterTuple

from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Instance as MInstance, Document, fields, validate


# temporary code
metadata = sa.MetaData()

tbl = sa.Table('tbl', metadata,
   sa.Column('id', sa.Integer, primary_key=True),
   sa.Column('val', sa.String(255)),
   # sa.Column('data', sa.Date(), nullable=True),
)


async def go():
    async with create_engine(user='postgres',
                             database='postgres',
                             host='127.0.0.1',
                             password='postgres') as engine:

        client = PostgresResource(engine, tbl)
        obj = Instance()
        obj.val = 'some1'

        res = await client.create(obj)

        print('res', res.__dict__)

        res.val = 'some2'
        res = await client.update(res.id, res)
        print('res', res.__dict__)

        # res = await client.create(obj)
        # res = await client.create(obj)
        # print('res', res.id)
        # print('res', await client.get_one(res.id))
        # print('res', await client.delete(res.id))
        # print('list', await client.get_list(limit=10))
        # print('list', await client.get_list())
        print('list', await client.get_many([25, 23, 22]))
        # print('order', await client.get_list(limit=10, order_by=sa.asc(tbl.c.id)))

        # column_name = i.get('column_name')
        # value = i.get('value')
        # filter_type_cls = i.get('filter')

        # print(
        #     'order',
        #     await client.get_list(
        #         filters=[
        #             FilterTuple('id', 5, "gte"),
        #             # FilterTuple('id', 10, "lte"),
        #             FilterTuple('val', "other", "like"),
        #         ]
        #     ),
        # )


# loop = asyncio.get_event_loop()
# loop.run_until_complete(go())


async def monog():
    db = AsyncIOMotorClient('0.0.0.0', 27017).test
    instance = MInstance(db)

    @instance.register
    class User(Document):
        email = fields.EmailField(required=True, unique=True)
        birthday = fields.DateTimeField(
            validate=validate.Range(min=datetime(1900, 1, 1)))
        # friends = fields.ListField(fields.ReferenceField("User"))

        class Meta:
            collection_name = "user"

    # res = await User(email='email@emila.com').commit()
    # print(res.inserted_id)
    # obj = Instance()
    # obj.email = 'email1@emila.com'
    #
    # client = MongoResource(User)
    # res = await client.create(obj)

    # print(res.__dict__)
    #
    # obj = Instance()
    # obj.email = 'email2@emila.com'
    #
    # res = await client.update(res.id, obj)
    # print(res.__dict__)
    # obj = Instance()
    # obj.email = 'email3@emila.com'
    # res = await client.create(obj)
    # obj = Instance()
    # obj.email = 'email3@emila.com'
    # res = await client.create(obj)
    # obj = Instance()
    # obj.email = 'email4@emila.com'
    # res = await client.create(obj)
    # obj = Instance()
    # obj.email = 'email5@emila.com'
    # res = await client.create(obj)
    # res = await client.get_one(res.id)
    # res = await client.delete(res.id)
    # print('list', await client.get_list(limit=5))
    # print('list', await client.get_many(
    #     ['5ec3870d8319dca59815497d', '5ec24134865a00ba7b2a8587']
    # ))
    # print('list', await client.get_list(limit=300))
    # print('list', await client.get_list(limit=5, offset=1))
    # print('list', await client.get_list(filters=[
    #     FilterTuple('email', 'email2@emila.com', 'eq')
    # ]))
    # print('list', await client.get_list(limit=5, order_by=[('_id', 1)]))
    # print('list', await client.get_list(limit=5, cursor='5ebbad7df1716e316e2701d2', order_by=[('_id', 1)]))

    # print(
    #     'order',
    #     await client.get_list(
    #         filters=[
    #             # FilterTuple('id', 5, "gte"),
    #             # FilterTuple('id', 10, "lte"),
    #             FilterTuple('email', "email3", "like"),
    #         ]
    #     ),
    # )
    # print("User: ", User, list(type(i) for i in User.schema.fields.values()))



# loop = asyncio.get_event_loop()
# loop.run_until_complete(monog())
#
#
# from aiohttp_admin2.mappers.base import Mapper
# from aiohttp_admin2.mappers.fields.common_fields import StringField, BooleanField
# from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
# from aiohttp_admin2.mappers.generics import MongoMapperGeneric
#
#
# class User(Document):
#     email = fields.EmailField(required=True, unique=True)
#     birthday = fields.DateTimeField(validate=validate.Range(min=datetime(1900, 1, 1)))
#
#
# class BookMapper(MongoMapperGeneric, table=User):
#     updated_at = StringField(required=True)
#
#
# print(BookMapper({"updated_at": 1}).fields)


# class BaseMapper(Mapper):
#     updated_at = StringField(required=True)
#
#
# class BookMapper(BaseMapper, Mapper):
#     title = StringField(required=True)
#     is_exist = BooleanField()
#
#
# print(list(BookMapper({}).fields))


# class BookMapper(PostgresMapperGeneric, table=tbl):
#     updated_at = StringField(required=True)
#
#
# print(BookMapper({"updated_at": 1}).fields)


from aiohttp import web
from aiohttp_admin2 import setup_admin
from aiohttp_admin2.view import TemplateView
from aiohttp_admin2.view import ControllerView
from aiohttp_admin2.controllers.controller import Controller
from aiohttp_admin2.resources.dict_resource.dict_resource import DictResource
from aiohttp_admin2.resources.postgres_resource.postgres_resource import PostgresResource


storage = {
    1: {"id": 1, "name": "Bob"},
    2: {"id": 2, "name": "Aliver"},
    3: {"id": 3, "name": "Aliver"},
    4: {"id": 4, "name": "Aliver"},
    5: {"id": 5, "name": "Aliver"},
    6: {"id": 6, "name": "Aliver"},
    7: {"id": 7, "name": "Aliver"},
    8: {"id": 8, "name": "Aliver"},
}


class BookController(Controller):
    resource = DictResource(storage)
    inline_fields = ['id', 'name']
    per_page = 3


class BookView(ControllerView):
    group_name: str = 'Controllers'
    controller = BookController


class NewPage(TemplateView):
    title = 'new page'
#
# class UserController(Controller):
#     resource = PostgresResource


app = web.Application()
# todo: test
setup_admin(
    app,
    views=[NewPage, BookView],
)

web.run_app(app)
