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
    pytest.param("postgres_manage", marks=pytest.mark.slow),
    pytest.param("mongo_manager", marks=pytest.mark.slow),
    # pytest.param("mysql_manager", marks=pytest.mark.slow),
    pytest.param("dict_manager"),
]

table = sa.Table('table', sa.MetaData(),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('val', sa.String(255), nullable=False),
 )


@pytest.fixture
async def postgres_manage(postgres):
    async with aiopg.sa.create_engine(**postgres) as engine:
        async with engine.acquire() as conn:
            await conn.execute(CreateTable(table))

            yield PostgresManager(table=table, engine=engine)

            await conn.execute(DropTable(table))


@pytest.fixture
async def mongo_manager(mongo):
    db = AsyncIOMotorClient(**mongo).test
    instance = MInstance(db)

    @instance.register
    class Table(Document):
        val = fields.StrField(required=True)

        class Meta:
            collection_name = "table"

    yield MongoManager(Table)


@pytest.fixture
async def mysql_manager(mysql):
    async with aiomysql.sa.create_engine(**mysql) as engine:
        async with engine.acquire() as conn:
            await conn.execute(CreateTable(table))

            yield MySqlManager(table=table, engine=engine)

            await conn.execute(DropTable(table))


@pytest.fixture
async def dict_manager():
    yield DictManager()


@pytest.fixture(params=managers_params)
def manager(request):
    yield request.getfixturevalue(request.param)
