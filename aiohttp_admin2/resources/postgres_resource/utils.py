import sqlalchemy as sa

from aiohttp_admin2.resources.exceptions import ClientException


__all__ = ["to_column", ]


def to_column(column_name: str, table: sa.Table) -> sa.Column:
    """
    Return sa.Column type from table by received column's name.

    Raises:
        ClientException: if received column doesn't exist in current table.
    """
    res = table.c.get(column_name)

    if res is None:
        raise ClientException(
            f"The {column_name} column does not exist in {table.name} table."
        )

    return res
