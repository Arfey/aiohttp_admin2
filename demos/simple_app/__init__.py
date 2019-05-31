from aiohttp import web
import aiohttp_admin2

if __name__ == '__main__':
    app = web.Application()

    aiohttp_admin2.setup(app)

    web.run_app(app)
