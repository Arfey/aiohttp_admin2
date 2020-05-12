import asyncio
from aiopg.sa import create_engine
import sqlalchemy as sa
from aiohttp_admin2.clients import PostgresClient
from aiohttp_admin2.clients import Instance


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
        print('res', res.id)
        print('res', await client.get_one(res.id))
        print('res', await client.delete(res.id))


loop = asyncio.get_event_loop()
loop.run_until_complete(go())
