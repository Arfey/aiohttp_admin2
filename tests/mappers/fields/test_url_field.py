import pytest

from aiohttp_admin2.mappers import Mapper
from aiohttp_admin2.mappers import fields


@pytest.mark.parametrize('input_data', [
    "http://localhost:8000/some/path/to",
    "http://foo.com/some/path/to",
    "https://foo.com/some/path/to",
    "https://www.foo.com/some/path/to",
    "https://www.foo.com/some/path/to.file_format",
    "https://www.foo.com/some/path/to.file_format",
])
@pytest.mark.parametrize('field_cls', [
    fields.UrlImageField,
    fields.UrlField,
    fields.UrlFileField,
])
def test_correct_url_type(field_cls, input_data):
    """
    In this test we check success convert to url type.
    """
    class InnerMapper(Mapper):
        field = field_cls()

    mapper = InnerMapper({"field": input_data})

    assert mapper.is_valid()
    assert mapper.data["field"] == input_data


@pytest.mark.parametrize('field_cls', [
    fields.UrlImageField,
    fields.UrlField,
    fields.UrlFileField,
])
def test_wrong_url_type(field_cls):
    """
    In this test we check handling of the wrong url type.
    """
    class InnerMapper(Mapper):
        field = field_cls()

    mapper = InnerMapper({"field": 'wrong_url'})
    assert not mapper.is_valid()
