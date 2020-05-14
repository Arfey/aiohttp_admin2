import asyncio
from aiopg.sa import create_engine
import sqlalchemy as sa
from aiohttp_admin2.clients import PostgresClient
from aiohttp_admin2.clients import MongoClient
from aiohttp_admin2.clients import Instance

from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Instance as MInstance, Document, fields, validate


# temporary code
metadata = sa.MetaData()

tbl = sa.Table('tbl', metadata,
   sa.Column('id', sa.Integer, primary_key=True),
   sa.Column('val', sa.String(255))
)


async def go():
    async with create_engine(user='postgres',
                             database='postgres',
                             host='127.0.0.1',
                             password='postgres') as engine:

        client = PostgresClient(engine, tbl)
        obj = Instance()
        obj.val = 'some'

        res = await client.create(obj)
        res = await client.create(obj)
        res = await client.create(obj)
        print('res', res.id)
        # print('res', await client.get_one(res.id))
        # print('res', await client.delete(res.id))
        print('list', await client.get_list(offset=0, limit=10))


loop = asyncio.get_event_loop()
loop.run_until_complete(go())


async def monog():
    db = AsyncIOMotorClient('0.0.0.0', 27017).test
    instance = MInstance(db)

    @instance.register
    class User(Document):
        email = fields.EmailField(required=True, unique=True)
        birthday = fields.DateTimeField(
            validate=validate.Range(min=datetime(1900, 1, 1)))
        friends = fields.ListField(fields.ReferenceField("User"))

        class Meta:
            collection_name = "user"

    # res = await User(email='email@emila.com').commit()
    # print(res.inserted_id)
    obj = Instance()
    obj.email = 'email@emila.com'

    client = MongoClient(User)
    res = await client.create(obj)
    res = await client.get_one(res.pk)
    res = await client.delete(res.pk)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(monog())
