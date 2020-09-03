import sqlalchemy as sa
from umongo import (
    MotorAsyncIOInstance,
    Document,
    fields as mongo_fields,
)

from aiohttp_admin2.mappers.generics import (
    PostgresMapperGeneric,
    MongoMapperGeneric,
)
from aiohttp_admin2.mappers import fields


metadata = sa.MetaData()


def test_generic_for_sql_alchemy_table():
    """
    In this test we check corrected work of auto generator for mapper from
    alchemy table.

        1. Generate corrected fields from table.
        2. Mixing generated fields and custom.
        3. Rewriting generated fields
    """
    tbl = sa.Table('tbl', metadata,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(255)),
    )

    class BookMapper(PostgresMapperGeneric, table=tbl):
        pass

    book = BookMapper({"id": 1, "title": "My test book1"})

    # 1. Generate corrected fields from table.
    assert len(book.fields) == 2

    assert isinstance(book.fields["id"], fields.IntField)
    assert isinstance(book.fields["title"], fields.StringField)

    # 2. Mixing generated fields and custom.
    class BookMapper(PostgresMapperGeneric, table=tbl):
        pages = fields.IntField()

    book = BookMapper({"id": 1, "title": "My test book2"})

    assert len(book.fields) == 3
    assert isinstance(book.fields["id"], fields.IntField)
    assert isinstance(book.fields["title"], fields.StringField)
    assert isinstance(book.fields["pages"], fields.IntField)

    # 3. Rewriting generated fields
    class BookMapper(PostgresMapperGeneric, table=tbl):
        id = fields.StringField()

    book = BookMapper({"id": 1, "title": "My test book3"})

    assert len(book.fields) == 2
    assert isinstance(book.fields["id"], fields.StringField)
    assert isinstance(book.fields["title"], fields.StringField)


def test_generic_for_umongo_table():
    """
    In this test we check corrected work of auto generator for mapper from
    umongo table.

        1. Generate corrected fields from table.
        2. Mixing generated fields and custom.
        3. Rewriting generated fields
    """
    instance = MotorAsyncIOInstance()

    @instance.register
    class User(Document):
        age = mongo_fields.IntegerField()
        email = mongo_fields.EmailField(required=True, unique=True)

    class UserMapper(MongoMapperGeneric, table=User):
        pass

    user = UserMapper({"age": 18, "email": "some@gmail.com"})

    # 1. Generate corrected fields from table. (with id field)
    assert len(user.fields) == 3

    assert isinstance(user.fields["age"], fields.IntField)
    assert isinstance(user.fields["email"], fields.StringField)

    # 2. Mixing generated fields and custom.
    class UserMapper(MongoMapperGeneric, table=User):
        some_field = fields.IntField()

    user = UserMapper({"age": 18, "email": "some@gmail.com"})

    assert len(user.fields) == 4
    assert isinstance(user.fields["email"], fields.StringField)
    assert isinstance(user.fields["age"], fields.IntField)
    assert isinstance(user.fields["some_field"], fields.IntField)

    # 3. Rewriting generated fields
    class UserMapper(MongoMapperGeneric, table=User):
        id = fields.IntField()

    user = UserMapper({"age": 18, "email": "some@gmail.com"})

    assert len(user.fields) == 3
    assert isinstance(user.fields["email"], fields.StringField)
    assert isinstance(user.fields["age"], fields.IntField)
    assert isinstance(user.fields["id"], fields.IntField)


def test_generic_validation_for_umongo_table():
    """
    In this test we check corrected work of mapper and marshmallow validation.

        1. Corrected work of marshmallow and generic validation together
        2. Corrected work of marshmallow validation
    """
    instance = MotorAsyncIOInstance()

    @instance.register
    class User(Document):
        age = mongo_fields.IntegerField()
        email = mongo_fields.EmailField(required=True, unique=True)

    class UserMapper(MongoMapperGeneric, table=User):
        other_field = fields.StringField(required=True)

    # 1. Corrected work of generic validation
    user = UserMapper({"age": 18, "email": "some@gmail.com"})

    assert not user.is_valid()
    assert not user.fields['age'].error
    assert not user.fields['email'].error
    assert user.fields['other_field'].error

    user = UserMapper({
        "age": 18,
        "email": "some@gmail.com",
        "other_field": "text",
    })

    assert user.is_valid()

    assert not user.fields['age'].error
    assert not user.fields['email'].error
    assert not user.fields['other_field'].error
    assert not user.error

    # 2. Corrected work of marshmallow validation
    user = UserMapper({
        "id": 1,
        "email": "text",
    })

    assert not user.is_valid()
    assert user.fields['age'].error
    assert user.fields['email'].error
