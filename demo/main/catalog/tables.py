from enum import Enum

import sqlalchemy as sa

from ..db import metadata


class GenreEnum(Enum):
    movie = 'movie'
    tv = 'tv'


class MovieStatusEnum(Enum):
    remorder = 'remorder'
    planned = 'planned'
    released = 'released'
    canceled = 'canceled'
    in_production = 'in production'
    post_production = 'post production'


class ShowStatusEnum(Enum):
    returning_series = 'returning series'
    in_production = 'in production'
    planned = 'planned'
    ended = 'ended'
    canceled = 'canceled'
    pilot = 'pilot'


class ImagesEnum(Enum):
    posters = 'posters'
    backdrops = 'backdrops'


movies_status_mapper = {
    i.value: i.name for i in MovieStatusEnum
}

shows_status_mapper = {
    i.value: i.name for i in ShowStatusEnum
}

actors = sa.Table('actors', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255), nullable=False),
    sa.Column('gender', sa.String(255), nullable=False),
    sa.Column('url', sa.String(255)),
)

actors_hash = sa.Table('actors_hash', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('actor_id', sa.ForeignKey('actors.id')),
    sa.Column('hash', sa.String(255)),
)

genres = sa.Table('genres', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
    sa.Column('type', sa.Enum(GenreEnum)),
)

movies = sa.Table('movies', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('title', sa.String(255), nullable=False),
    sa.Column('tag_line', sa.String(255)),
    sa.Column('overview', sa.Text),
    sa.Column('homepage', sa.String(255)),
    sa.Column('runtime', sa.Integer),
    sa.Column('budget', sa.Integer),
    sa.Column('revenue', sa.Integer),
    sa.Column('release_date', sa.Date),

    sa.Column('status', sa.Enum(MovieStatusEnum)),
    sa.Column('tmdb', sa.String),
    sa.Column('imdb', sa.String),
    sa.Column('vote_average', sa.SmallInteger),
    sa.Column('vote_count', sa.SmallInteger),
    sa.Column('poster_path', sa.String),
                  # media video
                  # media postgres
                  # media Backdrops
                  # score ???
)

movies_genres = sa.Table('movies_genres', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('genre_id', sa.ForeignKey('genres.id')),
    sa.Column('movie_id', sa.ForeignKey('movies.id')),
)

shows_genres = sa.Table('shows_genres', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('genre_id', sa.ForeignKey('genres.id')),
    sa.Column('show_id', sa.ForeignKey('shows.id')),
)

movies_actors = sa.Table('movies_actors', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('actor_id', sa.ForeignKey('actors.id')),
    sa.Column('movie_id', sa.ForeignKey('movies.id')),
    sa.Column('character', sa.String(255)),
    sa.Column('order', sa.Integer),
)

shows = sa.Table('shows', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('title', sa.String(255)),
    sa.Column('overview', sa.Text),
    sa.Column('homepage', sa.String(255)),
    sa.Column('tmdb', sa.String),
    sa.Column('poster_path', sa.String),
    sa.Column('vote_average', sa.SmallInteger),
    sa.Column('vote_count', sa.SmallInteger),
    sa.Column('first_air_date', sa.Date),
    sa.Column('last_air_date', sa.Date),
    sa.Column('status', sa.Enum(ShowStatusEnum)),
)

shows_seasons = sa.Table('shows_seasons', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('air_date', sa.Date),
    sa.Column('episode_count', sa.SmallInteger),
    sa.Column('season_number', sa.SmallInteger),
    sa.Column('name', sa.String),
    sa.Column('poster_path', sa.String),
    sa.Column('overview', sa.Text),
    sa.Column('show_id', sa.ForeignKey('shows.id')),
)

shows_actors = sa.Table('shows_actors', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('actor_id', sa.ForeignKey('actors.id')),
    sa.Column('movie_id', sa.ForeignKey('shows.id')),
    sa.Column('character', sa.String(255)),
    sa.Column('order', sa.Integer),
)

images_links = sa.Table('images_links', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('movie_id', sa.ForeignKey('movies.id')),
    sa.Column('show_id', sa.ForeignKey('shows.id')),
    sa.Column('url', sa.Text),
    sa.Column('type', sa.Enum(ImagesEnum)),
)
