from pathlib import Path
import base64
import asyncio
import os

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
from .auth.middlewares import admin_access_middleware
from .injectors import postgres_injector
from .load_data import (
    load_data,
    get_config_from_db_url,
)


THIS_DIR = Path(__file__).parent


async def load_data_cron(db_url_text: str) -> None:
    """
    Runner for sync data form tmdb database.
    """
    while True:
        if not os.getenv("WITHOUT_UPDATE_DB"):
            await load_data(db_url_text)

        # we need to sync data each 24 hours
        await asyncio.sleep(60 * 60 * 24)


async def jinja(application: web.Application) -> None:
    aiohttp_jinja2.setup(
        application,
        loader=jinja2.FileSystemLoader(str(THIS_DIR / 'templates')),
    )
    yield


async def security(application: web.Application) -> None:
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)

    session_setup(
        application,
        EncryptedCookieStorage(secret_key, cookie_name='API_SESSION'),
    )

    policy = SessionIdentityPolicy()
    setup_security(application, policy, AuthorizationPolicy())

    yield


async def database(application: web.Application) -> None:
    """
    A function that, when the server is started, connects to postgres,
    and after stopping it breaks the connection (after yield)
    """
    engine = await aiopg.sa\
        .create_engine(**get_config_from_db_url(application['db_url']))

    application['db'] = engine

    postgres_injector.init(engine)

    yield

    application['db'].close()
    await application['db'].wait_closed()


async def admin(application: web.Application) -> None:
    views = [
        # todo: add custom page
        ActorPage,
        GenresPage,
        MoviesPage,
        ShowsPage,
        UsersPage,
    ]
    setup_admin(
        application,
        views=views,
        middleware_list=[admin_access_middleware, ],
        logout_path='/logout',
    )


async def app():
    application = web.Application()
    application['db_url'] = os.getenv('DATABASE_URL')
    application.cleanup_ctx.extend([
        database,
        jinja,
        security,
    ])

    application.add_routes(routes)

    await admin(application)

    asyncio.create_task(load_data_cron(application['db_url']))

    return application
