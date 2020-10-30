import re

import aiohttp
import aiopg.sa
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from .db import metadata
from .catalog.tables import (
    actors,
    genres,
    movies,
    shows,
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
        pass

    async def get_detail_show(self, movie_id):
        """
        This method return full data connected with received show.
        """
        pass

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


async def load_data(db_url_text):
    config = get_config_from_db_url(db_url_text)

    recreate_tables(db_url_text)

    tmdb_client = TMDBClient(API_KEY)

    # Create genres
    query = genres\
        .insert()\
        .values([
            {
                'id': genre.get('id'),
                'name': genre.get('name'),
                'type': 'movie',
            } for genre in await tmdb_client.get_movie_genres()
        ])

    await execute(config, query)

    # query = genres\
    #     .insert()\
    #     .values([
    #         {
    #             'id': genre.get('id'),
    #             'name': genre.get('name'),
    #             'type': 'tv',
    #         } for genre in await tmdb_client.get_show_genres()
    #     ])
    #
    # await execute(config, query)

    # Create actors

    movies_dict = {}
    shows_dict = {}
    max_count_of_movies = 100

    for i in range(1, int(max_count_of_movies / 20)):
        res = await tmdb_client.get_movies(page=i)

        for movie in res:
            movies_dict[movie["id"]] = {
                "id": movie["id"],
                "name": movie["title"],
            }

    for i in range(1, int(max_count_of_movies / 20)):
        res = await tmdb_client.get_shows(page=i)

        for show in res:
            shows_dict[show["id"]] = {
                "id": show["id"],
                "name": show["name"],
            }

    actors_dict = {}

    for movie in movies_dict.keys():
        for cast in await tmdb_client.get_movie_credits(movie):
            actors_dict[cast["id"]] = {
                "name": cast["name"],
                "id": cast["id"],
            }

    for show in shows_dict.keys():
        for cast in await tmdb_client.get_show_credits(show):
            actors_dict[cast["id"]] = {
                "name": cast["name"],
                "id": cast["id"],
            }

    query = actors\
        .insert()\
        .values([
            {
                'id': actor.get('id'),
                'name': actor.get('name'),
            } for actor in actors_dict.values()
        ])

    await execute(config, query)

    query = movies\
        .insert()\
        .values([
            {
                'id': movie.get('id'),
                'name': movie.get('name'),
            } for movie in movies_dict.values()
        ])

    await execute(config, query)

    query = shows\
        .insert()\
        .values([
            {
                'id': show.get('id'),
                'name': show.get('name'),
            } for show in shows_dict.values()
        ])

    await execute(config, query)

    await execute(config, text("""
        SELECT setval('actors_id_seq', 10000000, true);
        SELECT setval('genres_id_seq', 10000000, true);
        SELECT setval('movies_id_seq', 10000000, true);
        SELECT setval('shows_id_seq', 10000000, true);
        SELECT setval('users_id_seq', 10000000, true);
    """))

    print('Done...')

