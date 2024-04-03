import pytest

from aiohttp_admin2.resources.exceptions import (
    ClientException,
    BadParameters,
)
from aiohttp_admin2.resources.types import FilterTuple

from .utils import generate_fake_instance


async def test_list_order(resource):
    """
    In this test check corrected work sort in get_list method of resource.

        1. Check default order
        2. Check asc order
        3. Error of ordering for cursor pagination
    """
    await generate_fake_instance(resource, 10)

    # 1. Check default order
    list_objects = await resource.get_list()

    assert len(list_objects.instances) == 10

    # 2. Check desc order
    list_objects_second = await resource.get_list(order_by='id')

    compare_list = zip(
        list_objects.instances,
        reversed(list_objects_second.instances),
    )

    for a, b in compare_list:
        assert a.get_pk() == b.get_pk()

    # 3. Error of ordering for cursor pagination
    with pytest.raises(ClientException):
        await resource.get_list(order_by='val', cursor=1)


@pytest.mark.parametrize("ordering", ("id", "-id"))
async def test_list_page_pagination(resource, ordering):
    """
    In this test check corrected work page pagination in get_list method of
    resource. + ordering

        1. Check of correct work page pagination

        - Check of correct work has_next and has_prev values
        - Check of correct work count value

        2. Check of correct work page pagination with remainder
    """
    instance_count = 9
    await generate_fake_instance(resource, instance_count)

    # 1. Check of correct work page pagination
    full_list_objects = \
        await resource.get_list(limit=instance_count, order_by=ordering)
    full_list_objects_ids = [i.get_pk() for i in full_list_objects.instances]

    assert len(full_list_objects_ids) == instance_count

    # page 1
    list_objects = await resource.get_list(limit=3, order_by=ordering)
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 3
    assert set(full_list_objects_ids[:3]) == set(list_objects_ids)

    # Check of correct work has_next and has_prev values
    assert list_objects.has_next
    assert not list_objects.has_prev
    assert list_objects.count == instance_count

    # page 2
    list_objects = await resource.get_list(limit=3, page=2, order_by=ordering)
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 3
    assert set(full_list_objects_ids[3:6]) == set(list_objects_ids)

    # Check of correct work has_next and has_prev values
    assert list_objects.has_next
    assert list_objects.has_prev
    assert list_objects.count == instance_count

    # page 3
    list_objects = await resource.get_list(limit=3, page=3, order_by=ordering)
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 3
    assert set(full_list_objects_ids[6:9]) == set(list_objects_ids)

    # Check of correct work has_next and has_prev values
    assert not list_objects.has_next
    assert list_objects.has_prev
    assert list_objects.count == instance_count

    # 2. Check of correct work page pagination with remainder
    await generate_fake_instance(resource, 1)

    # page 4
    list_objects = await resource.get_list(limit=3, page=4, order_by=ordering)
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 1

    # Check of correct work has_next and has_prev values
    assert not list_objects.has_next
    assert list_objects.has_prev


async def test_list_page_pagination_parameters_error(resource):
    """
    In this test check errors which can been raised if pass bad arguments.

        1. limit must be greater than zero
        2. cursor can't be use together with page
        3. page must be greater than zero
    """

    # 1. limit must be greater than zero
    with pytest.raises(BadParameters):
        await resource.get_list(limit=0)

    # 2. cursor can't be use together with page
    instances = await generate_fake_instance(resource, 1)

    with pytest.raises(BadParameters):
        await resource.get_list(page=2, cursor=instances[0].get_pk())

    # 3. page must be greater than zero
    with pytest.raises(BadParameters):
        await resource.get_list(page=0)


@pytest.mark.parametrize("ordering", ("id", "-id"))
async def test_list_cursor_pagination(resource, ordering):
    """
    In this test check corrected work cursor pagination in get_list method of
    resource. + ordering

        1. Check of correct work cursor pagination

        - Check of correct work has_next and has_prev values
        - Check of correct work count value

    """
    instance_count = 5
    await generate_fake_instance(resource, instance_count)

    # 1. Check of correct work cursor pagination
    full_list_objects = \
        await resource.get_list(limit=instance_count, order_by=ordering)
    full_list_objects_ids = [i.get_pk() for i in full_list_objects.instances]

    assert len(full_list_objects_ids) == instance_count

    # page 1
    list_objects = await resource.get_list(
        cursor=full_list_objects_ids[0],
        limit=3,
        order_by=ordering,
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 3
    assert set(full_list_objects_ids[1:4]) == set(list_objects_ids)

    assert list_objects.has_next
    assert list_objects.has_prev
    assert list_objects.count is None

    # page 2
    list_objects = await resource.get_list(
        cursor=full_list_objects_ids[3],
        limit=3,
        order_by=ordering,
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 1
    assert set(full_list_objects_ids[4:7]) == set(list_objects_ids)

    assert not list_objects.has_next
    assert list_objects.has_prev
    assert list_objects.count is None


async def test_filter_api_for_get_list(resource):
    """
    In this test check corrected work filter api in get_list method of resource.
    + ordering

        1. Check corrected work of one filter + ordering
        2. Check corrected work of two filter + ordering

    """
    # 1. Check corrected work of one filter + ordering
    instances = await generate_fake_instance(resource, 10)
    full_list_objects_ids = [i.get_pk() for i in instances]

    # desc
    list_objects = await resource.get_list(
        filters=[
            FilterTuple('id', full_list_objects_ids[0], "gt"),
        ],
        limit=len(full_list_objects_ids),
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert set(list_objects_ids) == set(full_list_objects_ids[1:])

    # asc
    list_objects = await resource.get_list(
        filters=[
            FilterTuple('id', full_list_objects_ids[-1], "lt"),
        ],
        limit=len(full_list_objects_ids),
        order_by='id'
    )
    asc_list_objects_ids = [i.get_pk() for i in list_objects.instances]

    for x, y in zip(list_objects_ids[1:], reversed(asc_list_objects_ids[1:])):
        assert x == y

    # 2. Check corrected work of two filter + ordering
    list_objects = await resource.get_list(
        filters=[
            FilterTuple('id', full_list_objects_ids[0], "gt"),
            FilterTuple('id', full_list_objects_ids[2], "lt"),
        ],
        limit=len(full_list_objects_ids),
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 1
    assert list_objects_ids[0] == full_list_objects_ids[1]


async def test_common_filters_for_get_list(resource):
    """
    In this test we check corrected work of common filters in get_list method
    of resource.

    Check corrected work of filters:
        eq, ne, lt, lte, gt, gte, in, nin, like
    """
    instances = await generate_fake_instance(resource, 10)
    full_list_objects_ids = [i.get_pk() for i in instances]

    # eq
    list_objects = await resource.get_list(
        filters=[
            FilterTuple('id', full_list_objects_ids[0], "eq"),
        ],
        limit=len(full_list_objects_ids),
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 1
    assert list_objects_ids[0] == full_list_objects_ids[0]

    # ne
    list_objects = await resource.get_list(
        filters=[
            FilterTuple('id', full_list_objects_ids[0], "ne"),
        ],
        limit=len(full_list_objects_ids),
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == len(full_list_objects_ids) - 1
    assert full_list_objects_ids[0] not in list_objects_ids

    # gt
    list_objects = await resource.get_list(
        filters=[
            FilterTuple('id', full_list_objects_ids[-2], "gt"),
        ],
        limit=len(full_list_objects_ids),
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 1
    assert list_objects_ids[0] == full_list_objects_ids[-1]

    # gte
    list_objects = await resource.get_list(
        filters=[
            FilterTuple('id', full_list_objects_ids[-2], "gte"),
        ],
        limit=len(full_list_objects_ids),
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 2
    assert set(list_objects_ids) == set(full_list_objects_ids[-2:])

    # lt
    list_objects = await resource.get_list(
        filters=[
            FilterTuple('id', full_list_objects_ids[1], "lt"),
        ],
        limit=len(full_list_objects_ids),
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 1
    assert list_objects_ids[0] == full_list_objects_ids[0]

    # lte
    list_objects = await resource.get_list(
        filters=[
            FilterTuple('id', full_list_objects_ids[1], "lte"),
        ],
        limit=len(full_list_objects_ids),
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 2
    assert set(list_objects_ids) == set(full_list_objects_ids[:2])

    # in
    ids = full_list_objects_ids[1], full_list_objects_ids[0]
    list_objects = await resource.get_list(
        filters=[
            FilterTuple('id', ids, "in"),
        ],
        limit=len(full_list_objects_ids),
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 2
    assert set(list_objects_ids) == set(ids)

    # nin
    list_objects = await resource.get_list(
        filters=[
            FilterTuple('id', ids, "nin"),
        ],
        limit=len(full_list_objects_ids),
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == len(full_list_objects_ids) - 2
    assert not (set(list_objects_ids) & set(ids))

    # like
    list_objects = await resource.get_list(
        filters=[
            FilterTuple('val', instances[0].data.val, "like"),
        ],
        limit=len(full_list_objects_ids),
    )
    list_objects_ids = [i.get_pk() for i in list_objects.instances]

    assert len(list_objects_ids) == 1
    assert list_objects_ids[0] == instances[0].get_pk()
