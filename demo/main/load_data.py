import re
import datetime

import aiohttp
import aiopg.sa
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from .db import metadata
from .auth.tables import users
from .catalog.tables import (
    actors,
    genres,
    movies,
    shows,
    movies_status_mapper,
    shows_status_mapper,
    movies_genres,
    movies_actors,
    shows_actors,
    shows_genres,
    shows_seasons,
    images_links,
    ImagesEnum,
)


table_list = [
    actors,
    genres,
    movies,
    shows,
]

# todo: move to secret
API_KEY = '702889df5a654ac187d0de04d5b85f97'


def get_config_from_db_url(text_url):
    result = re.match(
        r'postgres:\/\/(\w*):(\w*)@([-\w.]*):(\d*)\/([\w]*)',
        text_url,
    )

    user, password, host, port, database = result.groups()

    return {
        "user": user,
        "database": database,
        "host": host,
        "password": password,
        "port": port,
    }


class TMDBClient:
    API_URL = 'https://api.themoviedb.org/3'

    def __init__(self, api_key):
        self.api_key = api_key

    async def get(self, path, page=None):
        url = f'{self.API_URL}/{path}?api_key={self.api_key}'

        if page:
            url += f'&page={page}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()

    async def get_movies(self, page=1):
        """
        This function return common data connected with popular movies.
        """
        data = await self.get('movie/popular', page=page)

        return data["results"]

    async def get_shows(self, page=1):
        """
        This function return common data connected with popular shows.
        """
        data = await self.get('tv/popular', page=page)

        return data["results"]

    async def get_detail_movie(self, movie_id):
        """
        This method return full data connected with received movie.
        """
        return await self.get(f'movie/{movie_id}')

    async def get_detail_show(self, tv_id):
        """
        This method return full data connected with received show.
        """
        return await self.get(f'tv/{tv_id}]')

    async def get_shows_images(self, tv_id):
        return await self.get(f'tv/{tv_id}/images')

    async def get_movie_images(self, movie_id):
        return await self.get(f'movie/{movie_id}/images')

    async def get_movie_genres(self):
        """
        This method need to fetch all data connected with movie genres.
        """
        data = await self.get('genre/movie/list')

        return data["genres"]

    async def get_show_genres(self):
        """
        This method need to fetch all data connected with show genres.
        """
        data = await self.get('genre/tv/list')

        return data["genres"]

    async def get_movie_credits(self, movie_id):
        """
        This method need to fetch all data of movie credits.
        """
        data = await self.get(f'movie/{movie_id}/credits')

        return data["cast"]

    async def get_show_credits(self, show_id):
        """
        This method need to fetch all data of show credits.
        """
        data = await self.get(f'tv/{show_id}/credits')

        return data["cast"]


async def execute(config, command):
    async with aiopg.sa.create_engine(**config) as engine:
        async with engine.acquire() as conn:
            await conn.execute(command)


def recreate_tables(db_url):
    sync_engine = create_engine(
        db_url,
        isolation_level='AUTOCOMMIT',
    )

    # recreate tables
    metadata.drop_all(sync_engine)
    metadata.create_all(sync_engine)


async def create_users(config):
    query = users.insert().values([
        {
            "name": "admin",
            "is_superuser": True,
            "create_at": datetime.datetime.now(),
            "create_at_date": datetime.datetime.today(),
            "payload": {},
            "avatar": "https://bit.ly/2MZJnqt",
        },
        {
            "name": "user",
            "is_superuser": False,
            "create_at": datetime.datetime.now(),
            "create_at_date": datetime.datetime.today(),
            "payload": {},
            "avatar": "https://bit.ly/2MZJnqt",
        },
    ])

    await execute(config, query)


async def load_data(db_url_text):
    print("Start to load data ...")

    tmdb_client = TMDBClient(API_KEY)
    config = get_config_from_db_url(db_url_text)

    recreate_tables(db_url_text)

    # create users
    await create_users(config)

    # Create genres
    genres_ids_movie = [
        {
            'id': genre.get('id'),
            'name': genre.get('name'),
            'type': 'movie',
        } for genre in await tmdb_client.get_movie_genres()
    ]

    genres_ids_tv = [
        {
            'id': genre.get('id'),
            'name': genre.get('name'),
            'type': 'tv',
        } for genre in await tmdb_client.get_show_genres()
        if genre['id'] not in [i['id'] for i in genres_ids_movie]
    ]

    query = genres\
        .insert()\
        .values([*genres_ids_movie, *genres_ids_tv])

    await execute(config, query)

    # Create actors

    movies_dict = {}
    shows_dict = {}
    max_count_of_movies = 50

    for i in range(1, int(max_count_of_movies / 20)):
        res = await tmdb_client.get_movies(page=i)

        for movie in res:
            movies_dict[movie["id"]] = \
                await tmdb_client.get_detail_movie(movie["id"])

    for i in range(1, int(max_count_of_movies / 20)):
        res = await tmdb_client.get_shows(page=i)

        for show in res:
            shows_dict[show["id"]] = await tmdb_client\
                .get_detail_show(show["id"])

    actors_dict = {}
    movies_cast = []
    tv_cast = []

    for movie in movies_dict.keys():
        for cast in await tmdb_client.get_movie_credits(movie):
            actors_dict[cast["id"]] = {
                "name": cast["name"],
                "url": cast["profile_path"],
                "gender": cast["gender"],
                "id": cast["id"],
            }
            movies_cast.append({
                "actor_id": cast["id"],
                "movie_id": movie,
                "character": cast["character"],
                "order": cast["order"],
            })

    for show in shows_dict.keys():
        for cast in await tmdb_client.get_show_credits(show):
            actors_dict[cast["id"]] = {
                "name": cast["name"],
                "url": cast["profile_path"],
                "gender": cast["gender"],
                "id": cast["id"],
            }
            tv_cast.append({
                "actor_id": cast["id"],
                "show_id": show,
                "character": cast["character"],
                "order": cast["order"],
            })

    query = actors\
        .insert()\
        .values([
            {
                'id': actor.get('id'),
                'name': actor.get('name'),
                'url': actor.get('url'),
                'gender': "male" if actor.get('gender') == 1 else 'female',
            } for actor in actors_dict.values()
        ])

    await execute(config, query)

    data = [
            {
                'id': movie.get('id'),
                'tmdb': movie.get('id'),
                'imdb': movie.get('imdb_id'),
                'title': movie.get('title'),
                'tag_line': movie.get('tagline'),
                'overview': movie.get('overview'),
                'homepage': movie.get('homepage'),
                'runtime': movie.get('runtime'),
                'budget': movie.get('budget'),
                'revenue': movie.get('revenue'),
                'release_date': movie.get('release_date') or None,
                'vote_average': movie.get('vote_average'),
                'vote_count': movie.get('vote_count'),
                'poster_path': movie.get('poster_path'),
                'status': movies_status_mapper.get(
                    movie.get('status').lower()
                ),
            } for movie in movies_dict.values()
        ]

    query = movies\
        .insert()\
        .values(data)

    await execute(config, query)

    genres_movies_list = []
    for data in movies_dict.values():
        for genre in data["genres"]:
            genres_movies_list.append({
                "genre_id": genre.get("id"),
                "movie_id": data.get("id"),
            })

    # genres movies
    query = movies_genres\
        .insert() \
        .values([
        {
            'genre_id': data.get('genre_id'),
            'movie_id': data.get('movie_id'),
        } for data in genres_movies_list
    ])

    await execute(config, query)

    query = movies_actors\
        .insert() \
        .values([
        {
            'actor_id': actor.get('actor_id'),
            'movie_id': actor.get('movie_id'),
            'character': actor.get('character'),
            'order': actor.get('order'),
        } for actor in movies_cast
    ])

    await execute(config, query)

    movies_images_dict = {
        movie_id: await tmdb_client.get_movie_images(movie_id)
        for movie_id in movies_dict.keys()
    }

    movies_images_values = []

    for show_id, data in movies_images_dict.items():
        for backdrop in data.get('backdrops', []):
            movies_images_values.append({
                "movie_id": show_id,
                "type": ImagesEnum.backdrops,
                "url": backdrop.get('file_path')
            })

        for posters in data.get('posters', []):
            movies_images_values.append({
                "movie_id": show_id,
                "type": ImagesEnum.posters,
                "url": posters.get('file_path')
            })

    query = images_links \
        .insert() \
        .values(movies_images_values)

    await execute(config, query)

    shows_values = []
    shows_seasons_dict = {}

    for show in shows_dict.values():
        shows_values.append({
            'id': show.get('id'),
            'tmdb': show.get('id'),
            'first_air_date': show.get('first_air_date') or None,
            'last_air_date': show.get('last_air_date') or None,
            'overview': show.get('overview'),
            'homepage': show.get('homepage'),
            'title': show.get('name'),
            'vote_average': show.get('vote_average'),
            'vote_count': show.get('vote_count'),
            'poster_path': show.get('poster_path'),
            'status': shows_status_mapper.get(
                show.get('status').lower()
            ),
        })

        shows_seasons_dict[show.get('id')] = show.get('seasons')

    query = shows\
        .insert()\
        .values(shows_values)

    await execute(config, query)

    seasons_values = []

    for show_id, seasons in shows_seasons_dict.items():
        for season in seasons:
            seasons_values.append({"show_id": show_id, **season})

    query = shows_seasons\
        .insert()\
        .values(seasons_values)

    await execute(config, query)

    query = shows_actors\
        .insert() \
        .values([
        {
            'actor_id': actor.get('actor_id'),
            'movie_id': actor.get('show_id'),
            'character': actor.get('character'),
            'order': actor.get('order'),
        } for actor in tv_cast
    ])

    await execute(config, query)

    genres_show_list = []
    for data in shows_dict.values():
        for genre in data["genres"]:
            genres_show_list.append({
                "genre_id": genre.get("id"),
                "show_id": data.get("id"),
            })

    query = shows_genres\
        .insert() \
        .values([
        {
            'genre_id': data.get('genre_id'),
            'show_id': data.get('show_id'),
        } for data in genres_show_list
    ])

    await execute(config, query)

    shows_images_dict = {
        show_id: await tmdb_client.get_shows_images(show_id)
        for show_id in shows_dict.keys()
    }

    shows_images_values = []

    for show_id, data in shows_images_dict.items():
        for backdrop in data.get('backdrops', []):
            shows_images_values.append({
                "show_id": show_id,
                "type": ImagesEnum.backdrops,
                "url": backdrop.get('file_path')
            })

        for posters in data.get('posters', []):
            shows_images_values.append({
                "show_id": show_id,
                "type": ImagesEnum.posters,
                "url": posters.get('file_path')
            })

    query = images_links\
        .insert()\
        .values(shows_images_values)

    await execute(config, query)

    # set sequence value to so high to avoid problem with creating new
    # instances
    await execute(config, text("""
        SELECT setval('actors_id_seq', 10000000, true);
        SELECT setval('genres_id_seq', 10000000, true);
        SELECT setval('movies_id_seq', 10000000, true);
        SELECT setval('shows_id_seq', 10000000, true);
        SELECT setval('users_id_seq', 10000000, true);
    """))

    print('Done...')

