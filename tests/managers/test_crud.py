import pytest
from aiohttp_admin2.managers import Instance
from aiohttp_admin2.managers.exceptions import InstanceDoesNotExist
from aiohttp_admin2.managers import DictManager

from .utils import generate_fake_instance


# todo: add method to get pk from instance


@pytest.mark.asyncio
async def test_get_one(manager):
    """
    In this test check corrected work of get method in manager.

        1. Get corrected instance by id
        2. Get exception for instance which does not exist
    """
    instances = await generate_fake_instance(manager, 2)

    # 1. Get corrected instance by id
    first_id = instances[0].id
    second_id = instances[1].id

    first_instance = await manager.get_one(first_id)
    second_instance = await manager.get_one(second_id)

    assert first_id == first_instance.id
    assert second_id == second_instance.id

    # 2. Get exception of instance does not exist
    await manager.delete(second_id)

    with pytest.raises(InstanceDoesNotExist):
        await manager.get_one(second_id)


@pytest.mark.asyncio
async def test_delete(manager):
    """
    In this test check corrected work of delete method in manager.

        1. Get None for success delete object
        2. Get exception for instance which does not exist
    """
    # 1. Get None for success delete object
    instances = await generate_fake_instance(manager, 1)
    first_id = instances[0].id

    await manager.delete(first_id)

    # 2. Get exception for instance which does not exist
    with pytest.raises(InstanceDoesNotExist):
        await manager.delete(first_id)


@pytest.mark.asyncio
async def test_get_many(manager):
    """
    In this test check corrected work of get_many method in manager.

        1. Get existing instances
        2. Get non existing instances
        3. Get existing and non existing instances
    """

    def assert_bad_response(response):
        for key in response.keys():
            assert response[key].id == key

    # 1. Get existing instances
    instances = await generate_fake_instance(manager, 4)
    ids = [i.id for i in instances]

    res = await manager.get_many(ids)

    assert len(res) == 4
    assert_bad_response(res)

    # 2. Get non existing instances
    await manager.delete(ids[0])
    await manager.delete(ids[1])
    res = await manager.get_many(ids[0:2])

    assert len(res) == 0

    # 3. Get existing and non existing instances
    res = await manager.get_many(ids)

    assert len(res) == 2
    assert_bad_response(res)


@pytest.mark.asyncio
async def test_create(manager):
    """
    In this test check corrected work of create method in manager.

        1. Success create instance
        2. Create instance with error
    """

    # 1. Success create instance
    res = await generate_fake_instance(manager, 1)

    assert res[0].id

    # 2. Create instance with error
    if not isinstance(manager, DictManager):
        # dict manager doesn't raise any errors
        obj = Instance()

        with pytest.raises(Exception):
            await manager.create(obj)


@pytest.mark.asyncio
async def test_update(manager):
    """
    In this test check corrected work of update method in manager.

        1. Success update instance
        2. Update instance with error (unknown field)
    """

    # 1. Success update instance
    instances = await generate_fake_instance(manager, 1)
    instance = instances[0]

    instance.val = "new text"
    instance = await manager.update(instance.id, instance)

    assert instance.val == "new text"

    # 2. Update instance with error (unknown field)
    if not isinstance(manager, DictManager):
        instance.unknown_field = "unknown_field"

        with pytest.raises(Exception):
            await manager.update(instance.id, instance)
