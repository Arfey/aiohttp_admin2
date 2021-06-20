from aiohttp import web
from aiohttp_admin2 import setup_admin
from aiohttp_admin2.views import Admin
import aiohttp_jinja2
import jinja2
from pathlib import Path
import aiopg.sa

from .admin import CustomDashboard
from .admin import FirstCustomView
from .admin import UserView
from .admin import PostView
from .tables import postgres_injector


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


def app() -> web.Application:
    application = web.Application()

    application.cleanup_ctx.extend([
        init_db,
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
        views=[FirstCustomView, UserView, PostView]
    )

    return application


if __name__ == '__main__':
    web.run_app(app())
