from aiohttp_admin2.mappers import (
    fields,
    Mapper,
)
from aiohttp_admin2.mappers.exceptions import ValidationError


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
        created_at = fields.DateTime()

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
    assert book.fields["pages"].raw_value == 1
    assert book.fields["created_at"].raw_value == "Aug 28 1999 12:00AM"


# todo: multiple class with fields

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

    assert book.fields["title"].error
    assert not book.fields["description"].error

    # 2. mapper is valid if all required field is no empty
    book = BookMapping({
        "title": "value",
        "description": "",
    })

    assert book.is_valid(), \
        "title is not empty so mapper must be valid"

    assert not book.fields["title"].error
    assert not book.fields["description"].error


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
    assert not book.fields["title"].error
    assert not book.fields["description"].error
    assert not book.error

    # 2. test with error
    book = BookMapping(dict(title="Title", description="Title", pages=1))

    assert not book.is_valid()
    assert not book.fields["title"].error
    assert not book.fields["description"].error
    assert book.error

    # 3. test with mapper error and field error together
    book = BookMapping(
        dict(title="Title", description="Title")
    )

    assert not book.is_valid()
    assert not book.fields["title"].error
    assert not book.fields["description"].error
    assert book.error
    assert book.fields["pages"].error
