import sqlalchemy as sa

from ..db import metadata


actors = sa.Table('actors', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
)

genres = sa.Table('genres', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
)

movies = sa.Table('movies', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
)

shows = sa.Table('shows', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
)
