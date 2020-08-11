from pathlib import Path

from aiohttp import web
from aiohttp_admin2 import setup_admin
import aiopg.sa
import aiohttp_jinja2
import jinja2

from .admin.actors.controllers import ActorPage
from .admin.genres.controllers import GenresPage
from .admin.movies.controllers import MoviesPage
from .admin.shows.controllers import ShowsPage
from .admin.users.controllers import UsersPage
from .routes import routes
from .auth.views import login_page, login_handler


THIS_DIR = Path(__file__).parent


async def jinja(application: web.Application) -> None:
    aiohttp_jinja2.setup(
        application,
        loader=jinja2.FileSystemLoader(str(THIS_DIR / 'templates')),
    )
    yield


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
        jinja,
    ])

    application.add_routes(routes)

    await admin(application)

    return application
