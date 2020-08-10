import sqlalchemy as sa

from ..actors.table import metadata


shows = sa.Table('shows', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
)
