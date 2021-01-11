from enum import Enum

import sqlalchemy as sa

from ..db import metadata


class GenreEnum(Enum):
    movie = 'movie'
    tv = 'tv'


actors = sa.Table('actors', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
    sa.Column('gender', sa.String(255)),
)

genres = sa.Table('genres', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
    sa.Column('type', sa.Enum(GenreEnum)),
)

movies = sa.Table('movies', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
)

movies_actors = sa.Table('movies_actors', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('actor_id', sa.ForeignKey('actors.id')),
    sa.Column('movie_id', sa.ForeignKey('movies.id')),
)

shows = sa.Table('shows', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
)
