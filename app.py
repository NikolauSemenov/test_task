from aiohttp import web

from main.views import make_app


if __name__ == '__main__':
    web.run_app(make_app())