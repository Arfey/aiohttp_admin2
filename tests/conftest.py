from aiohttp import web
import pytest


@pytest.fixture
def app():
    """
    Initialization simple `aiohttp` application.
    """
    return web.Application()
