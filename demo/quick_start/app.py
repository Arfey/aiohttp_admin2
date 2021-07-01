from aiohttp import web
from aiohttp_admin2 import setup_admin
from aiohttp_admin2.views import Admin
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import setup as setup_security
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session import setup as session_setup
from cryptography import fernet
import base64
import aiohttp_jinja2
import jinja2
from pathlib import Path
import aiopg.sa

from .admin import CustomDashboard
from .admin import FirstCustomView
from .admin import UserView
from .admin import PostView
from .tables import postgres_injector
from .auth import admin_access_middleware
from .auth import login_page
from .auth import login_post
from .auth import logout_page
from .auth import AuthorizationPolicy


template_directory = Path(__file__).parent / 'templates'


class CustomAdmin(Admin):
    dashboard_class = CustomDashboard


async def init_db(app):
    engine = await aiopg.sa.create_engine(
        user='postgres',
        database='postgres',
        host='0.0.0.0',
        password='postgres',
    )
    postgres_injector.init(engine)
    app['db'] = engine

    yield

    app['db'].close()
    await app['db'].wait_closed()


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


def app() -> web.Application:
    application = web.Application()

    application.cleanup_ctx.extend([
        init_db,
        security,
    ])

    # setup jinja2
    aiohttp_jinja2.setup(
        app=application,
        loader=jinja2.FileSystemLoader(str(template_directory)),
    )

    # setup admin interface
    setup_admin(
        application,
        admin_class=CustomAdmin,
        views=[FirstCustomView, UserView, PostView],
        middleware_list=[admin_access_middleware, ],
        logout_path='/logout'
    )

    application.add_routes([
        web.get('/login', login_page, name='login'),
        web.post('/login', login_post, name='login_post'),
        web.get('/logout', logout_page, name='logout')
    ])

    return application


if __name__ == '__main__':
    web.run_app(app())
