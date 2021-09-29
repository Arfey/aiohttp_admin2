import pytest

from aiohttp_admin2.resources.exceptions import InstanceDoesNotExist

from .utils import generate_fake_instance


@pytest.mark.asyncio
async def test_get_one(resource):
    """
    In this test check corrected work of get method in resource.

        1. Get corrected instance by id
        2. Get exception for instance which does not exist
    """
    instances = await generate_fake_instance(resource, 2)

    # 1. Get corrected instance by id
    first_id = instances[0].get_pk()
    second_id = instances[1].get_pk()

    assert first_id and second_id

    first_instance = await resource.get_one(first_id)
    second_instance = await resource.get_one(second_id)

    assert first_id == first_instance.get_pk()
    assert second_id == second_instance.get_pk()

    # 2. Get exception of instance does not exist
    await resource.delete(second_id)

    with pytest.raises(InstanceDoesNotExist):
        await resource.get_one(second_id)


@pytest.mark.asyncio
async def test_get_one_correct_value_of_field(resource):
    """
    In this test we check that get method return instance with right value.
    """
    instances = await generate_fake_instance(resource, 1)

    value1 = instances[0].data.val
    value2 = instances[0].data.val2

    assert value1
    assert value2

    instance_from_db = await resource.get_one(instances[0].get_pk())
    assert instance_from_db.data.val == value1
    assert instance_from_db.data.val2 == value2
