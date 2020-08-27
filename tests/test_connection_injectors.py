from aiohttp_admin2.connection_injectors import ConnectionInjector
from aiohttp import web


async def test_connection_injector(aiohttp_client):
    """
    In this test we check corrected work of ConnectionInjector:

        1. success init in aiohttp context
        2. success inject into some decorated class
    """

    connection_injector = ConnectionInjector()
    db_connection_string = "db_connection_string"

    # 1. success init in aiohttp context
    async def init_db(_):
        connection_injector.init(db_connection_string)
        yield

    @connection_injector.inject
    class TestController:
        pass

    application = web.Application()
    application.cleanup_ctx.append(init_db)

    await aiohttp_client(application)

    assert isinstance(TestController.connection_injector, ConnectionInjector)
    assert \
        TestController.connection_injector.connection == db_connection_string
