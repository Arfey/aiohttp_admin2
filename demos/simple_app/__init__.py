import pathlib
from typing import (
    Dict,
    Any,
)

import aiohttp_jinja2
import jinja2
from aiohttp import web
import aiohttp_admin2

templates_dir = pathlib.Path(__file__).resolve().parent / 'templates'


@aiohttp_jinja2.template(template_name='index.html')
async def index_handler(req: web.Request) -> Dict[str, Any]:
    return {}

if __name__ == '__main__':
    app = web.Application()
    loader = jinja2.FileSystemLoader(str(templates_dir.absolute()))

    aiohttp_jinja2.setup(app, loader=loader)
    aiohttp_admin2.setup(app)

    app.add_routes([web.get('/', index_handler, name='index')])
    web.run_app(app)
