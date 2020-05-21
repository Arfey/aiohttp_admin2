import pytest

from aiohttp_admin2.managers import (
    PostgresManager,
    MongoManager,
    MySqlManager,
    DictManager,
    Instance,
)

dict_client = [DictManager, ]


@pytest.mark.parametrize('client', dict_client)
def test_corrected_implement_of_client(client):
    """
    In this test we check that all abstract methods in managers are implemented.
    """
    print('here', client)
    # client()


@pytest.mark.asyncio
@pytest.mark.parametrize('client', dict_client)
async def test_create_instance(client):
    """
    In this test we check a correct work of create method in client.

        1. Success created instance without errors.
        2. Generate primary key.
    """
    instance = Instance()
    instance.name = "Bob"

    # 1. Success created instance
    # data = await client().create(instance)

    # 2. Generate unique primary key.
    # assert data.pk


@pytest.mark.asyncio
async def test_update_instance():
    """
    In this test we check a correct work of update method in client.
    """


@pytest.mark.asyncio
async def test_get_one_instance():
    """
    In this test we check a correct work of get_one method in client.
    """


@pytest.mark.asyncio
async def test_get_many_instances():
    """
    In this test we check a correct work of get_many method in client.
    """


@pytest.mark.asyncio
async def test_get_list_of_instances():
    """
    In this test we check a correct work of get_list method in client.
    """


@pytest.mark.asyncio
async def test_delete_instance():
    """
    In this test we check a correct work of delete method in client.
    """


# todo: test for equal result from all managers


@pytest.mark.slow
def test_some(postgres, mongo, mysql):
    pass
