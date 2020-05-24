import asyncio

import pytest
import sqlalchemy as sa
from sqlalchemy.schema import (
    CreateTable,
    DropTable,
)
import aiopg.sa
import aiomysql.sa
from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Instance as MInstance, Document, fields

from aiohttp_admin2.managers import (
    PostgresManager,
    MySqlManager,
    MongoManager,
    DictManager,
)


managers_params = [
    pytest.param("postgres", marks=pytest.mark.slow),
    pytest.param("mongo", marks=pytest.mark.slow),
    # pytest.param("mysql", marks=pytest.mark.slow),
    # pytest.param("dict_manager"),
]

table = sa.Table('table', sa.MetaData(),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('val', sa.String(255), nullable=False),
 )


@pytest.yield_fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def postgres_manage(postgres):
    async with aiopg.sa.create_engine(**postgres) as engine:
        async with engine.acquire() as conn:
            await conn.execute(CreateTable(table))

            yield PostgresManager(table=table, engine=engine)

            await conn.execute(DropTable(table))


@pytest.fixture(scope="session")
async def mongo_manager(mongo):
    db = AsyncIOMotorClient(**mongo).test
    instance = MInstance(db)

    @instance.register
    class Table(Document):
        val = fields.StrField(required=True)

        class Meta:
            collection_name = "table"

    yield MongoManager(Table)


@pytest.fixture(scope='session')
async def mysql_manager(mysql):
    async with aiomysql.sa.create_engine(**mysql) as engine:
        async with engine.acquire() as conn:
            await conn.execute(CreateTable(table))

            yield MySqlManager(table=table, engine=engine)

            await conn.execute(DropTable(table))


@pytest.fixture
async def mongo(mongo_manager):
    print("mongo")
    yield mongo_manager
    mongo_manager.table.collection.delete_many({})


@pytest.fixture
async def postgres(postgres_manage):
    async with postgres_manage.engine.acquire() as conn:
        yield postgres_manage
        await conn.execute(postgres_manage.table.delete())


@pytest.fixture
async def mysql(mysql_manager):
    async with mysql_manager.engine.acquire() as conn:
        yield mysql_manager
        await conn.execute(mysql_manager.table.delete())


@pytest.fixture
async def dict_manager():
    yield DictManager()


@pytest.fixture(params=managers_params)
def manager(request):
    yield request.getfixturevalue(request.param)
