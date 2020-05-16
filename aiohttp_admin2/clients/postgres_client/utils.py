import sqlalchemy as sa

from aiohttp_admin2.exceptions import AdminException


def to_column(column_name: str, table: sa.Table) -> sa.Column:
    res = table.c.get(column_name)

    if res is None:
        # todo: corrected error
        raise AdminException(
            f"The column {column_name} does not exist in {table.name} table."
        )

    return res
