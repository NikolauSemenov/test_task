from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import alembic.config

from base import BaseView
from config import read_config

alembicArgs = [
    '--raiseerr',
    'upgrade', 'head',
]


class UserView(BaseView):

    async def get(self) -> web.Response:
        """
        Данная функция возвращает пользователей
        """
        return web.Response(body=f"{await self.db.get_users(self.session)}")

    async def post(self) -> web.Response:
        """
        Данная функция добавляет нового пользователя.
        """
        input_data = self.load(await self.request.json(), self.schemas.UserSchema())
        await self.db.save_users(self.session, input_data)
        alembic.config.main(argv=alembicArgs)
        return web.HTTPCreated()

    async def delete(self) -> web.Response:
        """
        Данная функция удаляет пользователя из бд по логину.
        """
        input_data = self.load(await self.request.json(), self.schemas.DeleteSchema())
        if await self.db.delete_user(self.session, input_data):
            alembic.config.main(argv=alembicArgs)
            return web.HTTPNoContent()
        return web.HTTPBadRequest()

    async def put(self) -> web.Response:
        """
        Данная функция обновляет имя и фамилию пользователя
        """
        input_data = self.load(await self.request.json(), self.schemas.UpdateSchema())
        await self.db.update_user(self.session, input_data)
        alembic.config.main(argv=alembicArgs)
        return web.HTTPOk()


def get_config():
    config = read_config()
    return config


async def connect_db(app: web.Application):
    config = get_config()['app']
    engine = create_async_engine(f"postgresql+asyncpg://{config['user']}:{config['password']}@{config['host']}/{config['namedb']}", echo=False)
    session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    session_db = session()
    app["session_db"] = session_db
    yield
    await session_db.close()


def make_app() -> web.Application:
    app = web.Application()
    app.router.add_view('/users', UserView)
    app.cleanup_ctx.append(connect_db)
    return app


if __name__ == '__main__':
    web.run_app(make_app())
