import sqlalchemy as sa

from ..db import metadata


users = sa.Table('users', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
    sa.Column('is_superuser', sa.Boolean),
)
