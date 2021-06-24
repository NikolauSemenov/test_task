from aiohttp import web, ClientSession
from aiohttp.web import View
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import get_users, save_users, load_data, delete_user, update_user
from serelizator import UserSchema, DeleteSchema, UpdateSchema


class UserView(View):

    async def get(self) -> web.Response:
        """
        Данная функция возвращает пользователей
        """
        # async with ClientSession() as session:
        #     async with session.get(self.request.url, get_users())
        return web.Response(body=f"{get_users()}")

    async def post(self) -> web.Response:
        """
        Данная функция добавляет нового пользователя.
        """

        # async with ClientSession() as session:
        #     async with session.post(self.request.url, json=await self.request.json()) as response:
        #         return response

        input_data = load_data(await self.request.json(), UserSchema())
        session_db = self.request.config_dict["session_db"]
        save_users(session_db, input_data)
        return web.HTTPCreated()

    async def delete(self) -> web.Response:
        """
        Данная функция удаляет пользователя из бд по логину.
        """
        input_data = load_data(await self.request.json(), DeleteSchema())
        db = self.request.config_dict["session_db"]
        if delete_user(db, input_data):
            return web.HTTPOk()
        return web.HTTPBadRequest()

    async def update(self) -> web.Response:
        """
        Данная функция обновляет имя и фамилию пользователя
        """
        input_data = load_data(await self.request.json(), UpdateSchema())
        db = self.request.config_dict["session_db"]
        update_user(db, input_data)
        return web.HTTPOk()


def setup(app: web.Application) -> None:
    app.cleanup_ctx.append(connect_db)


async def connect_db(app: web.Application):
    engine = create_engine('sqlite:///test.db', echo=False)
    Session = sessionmaker(bind=engine)
    session_db = Session()
    app["session_db"] = session_db
    yield
    await session_db.close()


def make_app():
    app = web.Application()
    app.router.add_view('/users', UserView)
    setup(app)
    return app


if __name__ == '__main__':
    web.run_app(make_app(), port=8080)