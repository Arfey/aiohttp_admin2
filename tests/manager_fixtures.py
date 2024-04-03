import asyncio

import pytest
import sqlalchemy as sa
from sqlalchemy.schema import (
    CreateTable,
    DropTable,
)
import aiopg.sa
import aiomysql.sa
# wait to fix problem with
# ImportError: Error importing plugin "tests.manager_fixtures": cannot import name 'coroutine' from 'asyncio'
# solution: update to motor ^3.0.0
# from motor.motor_asyncio import AsyncIOMotorClient
# from umongo.frameworks import MotorAsyncIOInstance
# from umongo import Document, fields

from aiohttp_admin2.resources import (
    PostgresResource,
    MySqlResource,
    # MongoResource,
    DictResource,
)


resource_params = [
    pytest.param("postgres", marks=pytest.mark.slow),
    # pytest.param("mongo", marks=pytest.mark.slow),
    pytest.param("mysql", marks=pytest.mark.slow),
    pytest.param("dict_resource"),
]

table = sa.Table('table', sa.MetaData(),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('val', sa.String(255), nullable=False),
    sa.Column('val2', sa.String(255), nullable=True),
)


@pytest.yield_fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    loop.set_debug(True)
    yield loop


@pytest.fixture(scope='session')
async def postgres_resource(postgres):
    async with aiopg.sa.create_engine(**postgres) as engine:
        async with engine.acquire() as conn:
            await conn.execute(CreateTable(table))

            yield PostgresResource(table=table, engine=engine)

            await conn.execute(DropTable(table))


@pytest.fixture(scope="session")
async def mongo_resource(mongo):
    # db = AsyncIOMotorClient(**mongo).test
    # instance = MotorAsyncIOInstance()
    # instance.set_db(db)

    # @instance.register
    # class Table(Document):
    #     val = fields.StrField(required=True)
    #     val2 = fields.StrField(required=False)

    #     class Meta:
    #         collection_name = "table"

    # yield MongoResource(Table)
    pass


@pytest.fixture(scope='session')
async def mysql_resource(mysql):
    asyncio.get_event_loop()
    async with aiomysql.sa.create_engine(**mysql) as engine:
        async with engine.acquire() as conn:
            await conn.execute(CreateTable(table))

            yield MySqlResource(table=table, engine=engine)

            # todo: fix problem with pymysql.err.ProgrammingError 1064
            # await conn.execute(DropTable(table))
            # await conn.execute('commit;')


@pytest.fixture
async def mongo(mongo_resource):
    yield mongo_resource
    mongo_resource.table.collection.delete_many({})


@pytest.fixture
async def postgres(postgres_resource):
    async with postgres_resource.engine.acquire() as conn:
        yield postgres_resource
        await conn.execute(postgres_resource.table.delete())


@pytest.fixture
async def mysql(mysql_resource):
    async with mysql_resource.engine.acquire() as conn:
        yield mysql_resource
        await conn.execute(mysql_resource.table.delete())
        await conn.execute('commit;')


@pytest.fixture
async def dict_resource():
    yield DictResource()


@pytest.fixture(params=resource_params)
def resource(request):
    return request.getfixturevalue(request.param)