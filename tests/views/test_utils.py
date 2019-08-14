"""
In this test file we check correct work of view's utils.
"""
from aiohttp.test_utils import make_mocked_request

from aiohttp_admin2.views.utils import getListParams
from aiohttp_admin2.types import SortDirectionEnum


def test_get_list_params():
    """
    In this test we check correct work of converting query string to
    the object.

        1. If a query sting is empty return object with default params
        2. if a query string is not empty return an object with correct
        params
    """
    # 1. If a query sting is empty return object with default params

    request_without_params = make_mocked_request('GET', '/base-list')
    res = getListParams(request_without_params)

    assert res.per_page == 50
    assert res.page == 1
    assert res.sort == 'user_id'
    assert res.sort_direction == SortDirectionEnum.ASC.value

    # 2. if a query string is not empty return an object with correct
    # params

    page = 2
    per_page = 3
    sort = 'name'
    sort_direction = SortDirectionEnum.DESC.value

    request_without_params = make_mocked_request(
        'GET',
        f'/base-list?page={page}&sort={sort}&sortDir={sort_direction}',
    )
    res = getListParams(request_without_params, per_page)

    assert res.per_page == per_page
    assert res.page == page
    assert res.sort == sort
    assert res.sort_direction == sort_direction
