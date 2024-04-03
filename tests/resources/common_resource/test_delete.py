import pytest

from aiohttp_admin2.resources.exceptions import InstanceDoesNotExist

from .utils import generate_fake_instance


async def test_delete(resource):
    """
    In this test check corrected work of delete method in resource.

        1. Get None for success delete object
        2. Get exception for instance which does not exist
    """
    # 1. Get None for success delete object
    instances = await generate_fake_instance(resource, 1)
    first_id = instances[0].get_pk()

    await resource.delete(first_id)

    # 2. Get exception for instance which does not exist
    with pytest.raises(InstanceDoesNotExist):
        await resource.delete(first_id)
