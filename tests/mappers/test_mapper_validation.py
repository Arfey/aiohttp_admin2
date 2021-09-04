import datetime

import pytest

from aiohttp_admin2.mappers import fields
from aiohttp_admin2.mappers import Mapper
from aiohttp_admin2.mappers.exceptions import ValidationError


FIELDS = [
    fields.FloatField,
    fields.ArrayField,
    fields.BooleanField,
    fields.ChoicesField,
    fields.DateTimeField,
    fields.DateField,
    fields.IntField,
    fields.SmallIntField,
    fields.LongStringField,
    fields.JsonField,
    fields.StringField,
    fields.UrlField,
    fields.UrlFileField,
    fields.UrlImageField,
]


def test_success_mapper():
    """
    In this test we check correct initialization of mapper and fields inside
    it.
        1. Simple initialize
        2. call `fields` method
        3. check `value` method into fields must converting to right type
        4. check `raw_value` method into fields must converting to right type
    """
    class BookMapping(Mapper):
        title = fields.StringField()
        description = fields.StringField()
        pages = fields.IntField()
        created_at = fields.DateTimeField()

    # 1. Simple initialize
    book = BookMapping({
        "title": "title value",
        "description": "description value",
        "pages": "1",  # <--- string value for test converting
        "created_at": "Aug 28 1999 12:00AM",  # <--- test converting to raw
    })

    # 2. call `fields` method
    assert len(book.fields) == 4, "BookMapping must has 4 fields"

    # 3. check `value` method into fields must converting to right type
    assert book.fields["title"].value == "title value"
    assert book.fields["description"].value == "description value"
    assert book.fields["pages"].value == 1

    # 3. check `raw_value` method into fields must converting to right type
    assert book.fields["title"].raw_value == "title value"
    assert book.fields["description"].raw_value == "description value"
    assert book.fields["pages"].raw_value == "1"
    assert book.fields["created_at"].raw_value == "Aug 28 1999 12:00AM"


def test_required_validation():
    """
    In this test we check correct work of required parameter in field object.

        1. mapper is invalid if required field is empty
        2. mapper is valid if all required field is no empty
    """
    class BookMapping(Mapper):
        title = fields.StringField(required=True)
        description = fields.StringField()

    # 1. mapper is invalid if required field is empty
    book = BookMapping({
        "title": "",
        "description": "",
    })

    assert not book.is_valid(), \
        "title is required field so mapper must be invalid"

    assert book.fields["title"].errors
    assert not book.fields["description"].errors

    # 2. mapper is valid if all required field is no empty
    book = BookMapping({
        "title": "value",
        "description": "",
    })

    assert book.is_valid(), \
        "title is not empty so mapper must be valid"

    assert not book.fields["title"].errors
    assert not book.fields["description"].errors


@pytest.mark.parametrize('field_cls', FIELDS)
def test_empty_value_for_required_field(field_cls):
    """
    In this test we check corrected work of `required` parameter for full list
    of fields. If value is empty and field is required we need to raise an
    error.
    """
    kwargs = {}

    if field_cls == fields.ArrayField:
        kwargs = {"field_cls": fields.IntField}

    if field_cls == fields.ChoicesField:
        kwargs = {"field_cls": fields.IntField, "choices": []}

    class FieldMapper(Mapper):
        field = field_cls(required=True, **kwargs)

    assert FieldMapper({}).is_valid() is False


@pytest.mark.parametrize('field_cls', FIELDS)
def test_empty_value_for_required_field_with_default(field_cls):
    """
    In this test we check corrected work of `required` parameter for full list
    of fields. If value is empty and field is required but field has default
    value then we need to use default.
    """
    default_values_map = {
        fields.FloatField: 1.,
        fields.IntField: 1,
        fields.SmallIntField: 1,
        fields.StringField: 'string',
        fields.LongStringField: 'string',
        fields.BooleanField: True,
        fields.UrlImageField: 'http://foo.com',
        fields.UrlField: 'http://foo.com',
        fields.UrlFileField: 'http://foo.com',
        fields.JsonField: '{"foo": "bar"}',
        fields.ArrayField: [1, 2],
        fields.ChoicesField: 'value',
        fields.DateTimeField: datetime.datetime.now(),
        fields.DateField: datetime.date.today(),
    }

    kwargs = {"default": default_values_map[field_cls]}

    if field_cls == fields.ArrayField:
        kwargs = {"field_cls": fields.IntField, **kwargs}

    if field_cls == fields.ChoicesField:
        kwargs = {
            "field_cls": fields.StringField,
            "choices": [('value', 'value')],
            **kwargs,
        }

    class FieldMapper(Mapper):
        field = field_cls(required=True, **kwargs)

    mapper = FieldMapper({})
    mapper.is_valid()

    assert FieldMapper({}).is_valid() is True


def test_main_mapper_validation():
    """
    In this test we check corrected work of main validation for mapper. This
    validation must run as additional validation together with fields
    validation and save as mapper error.

        1. test without error
        2. test with error
        3. test with mapper error and field error together
    """
    class BookMapping(Mapper):
        title = fields.StringField(required=True)
        description = fields.StringField(required=True)
        pages = fields.IntField(required=True)

        def validation(self):
            if self.fields['title'].value in self.fields['description'].value:
                raise ValidationError("title inside description")

    # 1. test without error
    book = BookMapping(dict(title="Title", description="Description", pages=1))

    assert book.is_valid()
    assert not book.fields["title"].errors
    assert not book.fields["description"].errors
    assert not book.error

    # 2. test with error
    book = BookMapping(dict(title="Title", description="Title", pages=1))

    assert not book.is_valid()
    assert not book.fields["title"].errors
    assert not book.fields["description"].errors
    assert book.error

    # 3. test with mapper error and field error together
    book = BookMapping(
        dict(title="Title", description="Title")
    )

    assert not book.is_valid()
    assert not book.fields["title"].errors
    assert not book.fields["description"].errors
    assert book.error
    assert book.fields["pages"].errors
