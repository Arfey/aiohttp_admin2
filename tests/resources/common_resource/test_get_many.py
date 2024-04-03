import pytest

from .utils import generate_fake_instance


async def test_get_many(resource):
    """
    In this test check corrected work of get_many method in resource.

        1. Get existing instances
        2. Get non existing instances
        3. Get existing and non existing instances
    """

    def get_len_not_none_values(d):
        return len([i for i in d.values() if i])

    def assert_bad_response(response, ids_list):
        for key in ids_list:
            assert response[key].get_pk() == key

    # 1. Get existing instances
    instances = await generate_fake_instance(
        resource,
        # generate more then we need to check that we'll get correct items
        6,
    )
    ids = [i.get_pk() for i in instances[:4]]

    res = await resource.get_many(ids)

    assert get_len_not_none_values(res) == 4
    assert len(res) == 4
    assert_bad_response(res, ids)

    # 2. Get non existing instances
    await resource.delete(ids[0])
    await resource.delete(ids[1])

    res = await resource.get_many(ids[:2])
    assert get_len_not_none_values(res) == 0
    # we need return dict with `None` values for corrected work
    assert len(res) == 2

    # 3. Get existing and non existing instances
    res = await resource.get_many(ids)

    assert get_len_not_none_values(res) == 2
    assert_bad_response(res, ids[2:])
    assert len(res) == 4
