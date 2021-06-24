from aiohttp import web
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from base import BaseView


class UserView(BaseView):

    async def get(self) -> web.Response:
        """
        Данная функция возвращает пользователей
        """
        return web.Response(body=f"{self.db.get_users(self.session)}")

    async def post(self) -> web.Response:
        """
        Данная функция добавляет нового пользователя.
        """
        input_data = self.load(await self.request.json(), self.schemas.UserSchema())
        self.db.save_users(self.session, input_data)
        return web.HTTPCreated()

    async def delete(self) -> web.Response:
        """
        Данная функция удаляет пользователя из бд по логину.
        """
        input_data = self.load(await self.request.json(), self.schemas.DeleteSchema())
        if self.db.delete_user(self.session, input_data):
            return web.HTTPOk()
        return web.HTTPBadRequest()

    async def update(self) -> web.Response:
        """
        Данная функция обновляет имя и фамилию пользователя
        """
        input_data = self.load(await self.request.json(), self.schemas.UpdateSchema())
        self.db.update_user(self.session, input_data)
        return web.HTTPOk()


async def connect_db(app: web.Application):
    engine = create_engine('sqlite:///test.db', echo=False)
    Session = sessionmaker(bind=engine)
    session_db = Session()
    app["session_db"] = session_db
    yield
    session_db.close()


def make_app():
    app = web.Application()
    app.router.add_view('/users', UserView)
    app.cleanup_ctx.append(connect_db)
    return app


if __name__ == '__main__':
    web.run_app(make_app(), port=8080)
