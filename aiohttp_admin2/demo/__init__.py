from pathlib import Path
import base64

from cryptography import fernet
from aiohttp import web
from aiohttp_admin2 import setup_admin
from aiohttp_security import (
    SessionIdentityPolicy,
    setup as setup_security,
)
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import aiopg.sa
import aiohttp_jinja2
import jinja2

from .admin.actors.controllers import ActorPage
from .admin.genres.controllers import GenresPage
from .admin.movies.controllers import MoviesPage
from .admin.shows.controllers import ShowsPage
from .admin.users.controllers import UsersPage
from .routes import routes
from .auth.views import login_page
from .auth.authorization import AuthorizationPolicy


THIS_DIR = Path(__file__).parent


async def jinja(application: web.Application) -> None:
    aiohttp_jinja2.setup(
        application,
        loader=jinja2.FileSystemLoader(str(THIS_DIR / 'templates')),
    )
    yield


async def security(application: web.Application) -> None:
    policy = SessionIdentityPolicy()
    setup_security(application, policy, AuthorizationPolicy())

    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    session_setup(application, EncryptedCookieStorage(secret_key))

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
        security,
    ])

    application.add_routes(routes)

    await admin(application)

    return application
