import pytest
import typing as t
from aiohttp_admin2.managers import Instance
from aiohttp_admin2.managers.exceptions import InstanceDoesNotExist


# todo: add method to get pk from instance


async def generate_fake_instance(manager, n: int = 1) -> t.List[Instance]:
    instances: t.List[Instance] = []

    for _ in range(n):
        obj = Instance()
        obj.val = 'some1'

        instances.append(await manager.create(obj))

    return instances


@pytest.mark.asyncio
async def test_create_instance(manager):
    obj = Instance()
    obj.val = 'some1'

    res = await manager.create(obj)
    print(res)


@pytest.mark.asyncio
async def test_get_instance_by_id(manager):
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
async def test_get_instance_by_id(manager):
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
    # todo: add exception
    # with pytest.raises(InstanceDoesNotExist):
    #     await manager.delete(first_id)
