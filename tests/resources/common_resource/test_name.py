import pytest


async def test_name_property(resource):
    """
    In this test check corrected generate name of resource. This name will use
    for admin interface so it's so important.
    """
    assert resource.name
