import pytest

from aiohttp_admin2.resources import DictResource

from tests.resources.common_resource.utils import generate_fake_instance


@pytest.mark.asyncio
async def test_update(resource):
    """
    In this test check corrected work of update method in resource.

        1. Success update instance
        2. Update instance with error (unknown field)
    """

    # 1. Success update instance
    instances = await generate_fake_instance(resource, 1)
    instance = instances[0]

    instance.data.val = "new text"
    instance = await resource.update(instance.get_pk(), instance)

    assert instance.data.val == "new text"

    # 2. Update instance with error (unknown field)
    if not isinstance(resource, DictResource):
        instance.data = {"unknown_field":  "unknown_field"}

        with pytest.raises(Exception):
            await resource.update(instance.get_pk(), instance)
