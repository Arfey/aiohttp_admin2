import pytest

from aiohttp_admin2.resources import Instance
from aiohttp_admin2.resources import DictResource


async def test_create_with_success(resource):
    """
    In this test check corrected work of create method in resource.

        Success create instance
    """

    obj = Instance()
    obj.data = {"val": 'test', "val2": "test2"}

    instance = await resource.create(obj)

    assert instance.data.val == 'test'
    assert instance.data.val2 == 'test2'

    assert instance.get_pk()


async def test_create_success_with_partial_data(resource):
    """
    In this test we check that instance have been created success without full
    values.
    """
    obj = Instance()
    obj.data = {"val": 'test'}

    instance = await resource.create(obj)

    assert instance.get_pk()
    assert instance.data.val == 'test'
    assert getattr(instance.data, 'val2', None) is None


async def test_create_with_error_if_data_no_precent_required_field(resource):
    """
    In this test we check that instance will not be create if data don't have
    required fields.
    """
    obj = Instance()
    obj.data = {"val2": 'test2'}

    if not isinstance(resource, DictResource):
        with pytest.raises(Exception):
            await resource.create(obj)


async def test_create_with_error(resource):
    """
    In this test check corrected work of create method in resource.

        Create instance with error:

            1. Instance without data
            2. Instance with empty values
    """

    # 1. Instance without data
    if not isinstance(resource, DictResource):
        # dict resource doesn't raise any errors
        obj = Instance()

        with pytest.raises(Exception):
            await resource.create(obj)

    # 2. Instance with empty values
    if not isinstance(resource, DictResource):
        # dict resource doesn't raise any errors
        obj = Instance()
        obj.data = {}

        with pytest.raises(Exception):
            await resource.create(obj)
