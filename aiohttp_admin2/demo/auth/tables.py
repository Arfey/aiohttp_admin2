import sqlalchemy as sa

from ..db import metadata


users = sa.Table('users', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
    sa.Column('is_superuser', sa.Boolean),
    sa.Column('array_c', sa.ARRAY(sa.Integer)),
    sa.Column('create_at', sa.DateTime()),
    sa.Column('create_at_date', sa.Date()),
)
