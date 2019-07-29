import sqlalchemy as sa
from aiohttp_admin2.core import fields
from aiohttp_admin2.core.forms import BaseForm


__all__ = ['PostgresAdminForm', ]


DEFAULT_FIELD = fields.TextField
POSTGRES_MAPPING = {
    sa.Integer: fields.IntegerField,
    sa.Text: fields.TextField,
}


class PostgresAdminForm(BaseForm):
    """
    This class help to generate a form from a slqAlchemy table for
    the PostgresSQL.
    """
    def __init_subclass__(cls, table: sa.Table) -> None:
        get_fields = {
            key: POSTGRES_MAPPING.get(type(value.type), DEFAULT_FIELD)
            for key, value in table.columns.items()
        }

        for name, Field in get_fields.items():
            if not hasattr(cls, name):
                cls._class_fields.update({name: Field(name=name)})
