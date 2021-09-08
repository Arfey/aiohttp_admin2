import pytest
import sqlalchemy as sa

from aiohttp_admin2.resources.postgres_resource.utils import to_column
from aiohttp_admin2.resources.exceptions import ClientException


table = sa.Table('test_table', sa.MetaData(),
    sa.Column('int', sa.Integer, primary_key=True),
    sa.Column('string', sa.String(255)),
    sa.Column('bool', sa.Boolean),
    sa.Column('array', sa.ARRAY(sa.Integer)),
    sa.Column('datetime', sa.DateTime),
    sa.Column('date', sa.Date),
    sa.Column('json', sa.JSON),
    sa.Column('text', sa.Text),
)


@pytest.mark.parametrize('name, column', [
    ('int', table.c['int']),
    ('string', table.c['string']),
    ('bool', table.c['bool']),
    ('array', table.c['array']),
    ('datetime', table.c['datetime']),
    ('date', table.c['date']),
    ('text', table.c['text']),
    ('json', table.c['json']),
])
def test_get_existing_field(name, column):
    """
    In this test we check that to_column function success return a column from
    a table by the column's name
    """
    assert to_column(name, table) == column


def test_raise_an_error_if_column_does_not_exist():
    """
    In this test we check tha to_column function raise an error if table
    doesn't exist column with received name.
    """
    with pytest.raises(ClientException):
        to_column("bad_field", table)
