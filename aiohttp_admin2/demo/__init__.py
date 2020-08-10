from aiohttp import web
from aiohttp_admin2 import setup_admin
import aiopg.sa

from .admin.actors.controllers import ActorPage
from .admin.genres.controllers import GenresPage
from .admin.movies.controllers import MoviesPage
from .admin.shows.controllers import ShowsPage
from .admin.users.controllers import UsersPage


async def database(application: web.Application) -> None:
    """
    A function that, when the server is started, connects to postgres,
    and after stopping it breaks the connection (after yield)
    """
    engine = await aiopg.sa.create_engine(
        user='postgres',
        database='postgres',
        host='0.0.0.0',
        password='postgres',
    )
    application['db'] = engine

    yield

    application['db'].close()
    await application['db'].wait_closed()


async def admin(application: web.Application) -> None:
    # todo: setup engine without it
    engine = await aiopg.sa.create_engine(
        user='postgres',
        database='postgres',
        host='0.0.0.0',
        password='postgres',
    ).__aenter__()

    setup_admin(
        application,
        engines={
            "db": engine
        },
        views=[
            # todo: add custom page
            ActorPage,
            GenresPage,
            MoviesPage,
            ShowsPage,
            UsersPage,
        ],
    )


async def app():
    application = web.Application()
    application.cleanup_ctx.extend([
        database,
    ])

    await admin(application)

    return application
