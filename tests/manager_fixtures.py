import asyncio
import contextvars

import aiomysql.sa
import aiopg.sa
import pytest
import sqlalchemy as sa
from pytest_asyncio import is_async_test
from sqlalchemy.schema import (
    CreateTable,
    DropTable,
)

from aiohttp_admin2.resources import (
    DictResource,
    PostgresResource,
)
from aiohttp_admin2.resources.mysql_resource.mysql_resource import (
    MySqlResource,
)

# wait to fix problem with
# ImportError: Error importing plugin "tests.manager_fixtures": cannot import name 'coroutine' from 'asyncio'
# solution: update to motor ^3.0.0
# from motor.motor_asyncio import AsyncIOMotorClient
# from umongo.frameworks import MotorAsyncIOInstance
# from umongo import Document, fields

# from aiohttp_admin2.resources.mongo_resource.mongo_resource import MongoResource


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

test_context = contextvars.Context()


def pytest_collection_modifyitems(items):
    # fix how to use the same loop for each test
    # https://pytest-asyncio.readthedocs.io/en/v0.24.0/how-to-guides/run_session_tests_in_same_loop.html
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture(scope="session")
def event_loop_policy():
    # fix how to use the same context for each test
    # https://github.com/pytest-dev/pytest-asyncio/issues/127#issuecomment-2062158881
    class CustomEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
        def task_factory(self, loop, coroutine):
            return asyncio.Task(coroutine, loop=loop, context=test_context)

        def new_event_loop(self):
            loop = self._loop_factory()
            loop.set_task_factory(self.task_factory)
            return loop

    policy = CustomEventLoopPolicy()

    yield policy

    policy.get_event_loop().close()


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
