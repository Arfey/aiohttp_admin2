import pathlib
from typing import (
    Dict,
    Any,
)

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_admin2.base import Admin

templates_dir = pathlib.Path(__file__).resolve().parent / 'templates'


@aiohttp_jinja2.template(template_name='index.html')
async def index_handler(req: web.Request) -> Dict[str, Any]:
    app = req.app
    return {}

if __name__ == '__main__':
    app = web.Application()
    loader = jinja2.FileSystemLoader(str(templates_dir.absolute()))
    aiohttp_jinja2.setup(app, loader=loader)

    Admin(app)

    app.add_routes([web.get('/', index_handler, name='index')])
    web.run_app(app)
