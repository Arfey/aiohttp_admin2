import pytest

from aiohttp_admin2.resources import Instance
from aiohttp_admin2.resources import DictResource


@pytest.mark.asyncio
async def test_create(resource):
    """
    In this test check corrected work of create method in resource.

        1. Success create instance
        2. Create instance with error
    """

    # 1. Success create instance
    obj = Instance()
    obj.data = {"val": 'test'}

    instance = await resource.create(obj)

    assert instance.get_pk()

    # 2. Create instance with error
    if not isinstance(resource, DictResource):
        # dict resource doesn't raise any errors
        obj = Instance()

        with pytest.raises(Exception):
            await resource.create(obj)
