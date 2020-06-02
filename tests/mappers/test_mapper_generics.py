import sqlalchemy as sa

from aiohttp_admin2.mappers.generics import PostgresMapperGeneric
from aiohttp_admin2.mappers import fields


metadata = sa.MetaData()


def test_generic_for_sql_alchemy_table():
    """
    In this test we check corrected work of auto generator for mapper.

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
    print(book.fields)
    # todo: fixed problem with nested fields
    assert isinstance(book.fields["id"], fields.StringField)
    assert isinstance(book.fields["title"], fields.StringField)


# todo: test for mongo generator
