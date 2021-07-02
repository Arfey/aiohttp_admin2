from pathlib import Path
import base64
import asyncio
import os

from cryptography import fernet
import aiohttp
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
from motor.motor_asyncio import AsyncIOMotorClient

from .admin.actors.controllers import ActorPage
from .admin.genres.pages import GenresPage
from .admin.movies.pages import MoviesPage
from .admin.template_view import TemplatePage
from .admin.shows.controllers import ShowsPage
from .admin.users.controllers import UsersPage
from .admin.mongo_admin import MongoPage
from .routes import routes
from .auth.views import login_page
from .auth.authorization import AuthorizationPolicy
from .auth.middlewares import admin_access_middleware
from .admin.injectors import (
    postgres_injector,
    instance,
)
from .load_data import (
    load_data,
    get_config_from_db_url,
)


THIS_DIR = Path(__file__).parent
static_dir = THIS_DIR / 'static'


async def load_data_cron(db_url_text: str) -> None:
    """
    Runner for sync data form tmdb database.
    """
    while True:
        if not os.getenv("WITHOUT_UPDATE_DB"):
            await load_data(db_url_text)

        # we need to sync data each 24 hours
        await asyncio.sleep(60 * 60 * 24)


async def ping_website() -> None:
    """
    if have not been any request then heroku will shot down pod. to prevent it
    we'll ping website each 10 minutes
    """
    website_url = 'https://shrouded-stream-28595.herokuapp.com'
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(website_url):
                await asyncio.sleep(60 * 10)


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


async def mongo(application: web.Application) -> None:
    """
    A function that, when the server is started, connects to mongo,
    and after stopping it breaks the connection (after yield)
    """

    conn = AsyncIOMotorClient(
        'mongodb://0.0.0.0:27017/db',
        io_loop=asyncio.get_event_loop(),
    )

    application['mongo'] = conn.get_database()
    instance.set_db(application['mongo'])

    yield

    application['mongo'].client.close()


async def admin(application: web.Application) -> None:
    views = [
        ActorPage,
        GenresPage,
        MoviesPage,
        ShowsPage,
        UsersPage,
        # MongoPage,
        TemplatePage,
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
        # mongo,
        jinja,
        security,
    ])

    application.router\
        .add_static('/static/', path=str(static_dir), name='static')

    application.add_routes(routes)

    await admin(application)

    asyncio.create_task(load_data_cron(application['db_url']))
    asyncio.create_task(ping_website())

    return application
