import datetime
import time
import base64

from cryptography import fernet
from aiohttp import web
from aiohttp.web import View
from marshmallow import Schema
from multidict import MultiDictProxy
from sqlalchemy import exc
from aiohttp_session import get_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from marshmallow.exceptions import ValidationError

from connect_db import DatabaseTransaction
from models import UsersClass, RulesClass
from logger_app import LoggingMain
from serelizator import UserSchema

logger = LoggingMain().get_logging('Test_task')


class UserView(View):

    @staticmethod
    async def startup_1(app):
        print(1)

    @staticmethod
    async def cleanup_ctx_2(app):
        print('init 2')
        yield
        print('cleanup 2')

    @staticmethod
    async def startup_3(app):
        print('init 3')

    def get_connect_db(self):
        """
        Осуществляется подключение к бд
        """
        try:
            return DatabaseTransaction('test.db')
        except:
            return False

    # TODO: Если хотел использовать отдельную функцию для валидации схем, то нужно было сделать как то так
    # noinspection PyMethodMayBeStatic
    def load_data(self, data: MultiDictProxy, schema: Schema) -> dict:
        """
        Данная функция проверяет входные данные
        """
        # try:
        return schema.load(data)
        # except ValidationError as e:
        #     logger.error(f"{e}")
        #     raise web.HTTPUnprocessableEntity()

    async def get(self) -> web.Response:
        """
        Данная функция возвращает пользователей
        """

        connect_db = self.get_connect_db()
        with connect_db as db_connect:
            with db_connect as cursor:
                query = cursor.query(UsersClass).all()
                return web.Response(body=f"{query}")

    async def post(self) -> web.Response:
        """
        Данная функция добавляет нового пользователя.
        """

        input_data = self.load_data(self.request.query, UserSchema())
        connect_db = self.get_connect_db()

        try:
            birthday = datetime.datetime.strptime(input_data['birthday'], '%Y-%m-%d')
            users = UsersClass(
                name=input_data['name'],
                last_name=input_data['last_name'],
                login=input_data['login'],
                password=input_data['password'],
                birthday=birthday
            )

            with connect_db as db_connect:
                with db_connect as session:
                    session.add(users)
                    session.flush()

                    query = session.query(UsersClass).filter_by(login=input_data['login']).first()
                    admin_flag = input_data['admin_flag']
                    rules = RulesClass(
                        block=False,
                        admin=admin_flag,
                        only_read=False if admin_flag is True else True,
                        user_id=query.id
                    )

                    session.add(rules)
                    session.commit()

        except exc.IntegrityError as e:
            logger.error(f"{e}")
            raise web.HTTPForbidden()

        except exc.PendingRollbackError as e:
            logger.error(f"{e}")
            raise web.HTTPForbidden()

        except KeyError as e:
            logger.error(f"{e}")
            raise web.HTTPForbidden()

        return web.Response(body='Пользователь успешно создан')

    async def delete(self) -> web.Response:
        """
        Данная функция удаляет пользователя из бд по логину.
        """
        input_data = self.load_data(self.request.query, UserSchema())
        connect_db = self.get_connect_db()

        if input_data:
            with connect_db as db_connect:
                with db_connect as session:
                    query = session.query(UsersClass, RulesClass).filter_by(login=input_data['login']).first()
                    if query is not None:
                        session.delete(query[1])
                        session.delete(query[0])

                        session.commit()
                        return web.Response(body='Пользователь успешно удален')

        raise web.HTTPForbidden()

    async def update(self) -> web.Response:
        """
        Данная функция обновляет имя и фамилию пользователя
        """
        input_data = self.load_data(self.request.query, UserSchema())
        connect_db = self.get_connect_db()

        try:
            if input_data:
                with connect_db as db_connect:
                    with db_connect as session:
                        query = session.query(UsersClass).filter(UsersClass.login == input_data['login']).one()
                        query.name = input_data['name']
                        query.last_name = input_data['last_name']

                        return web.Response(body='Пользователь успешно обновлен')

        except KeyError as e:
            logger.error(f"{e}")
            raise web.HTTPForbidden()


def make_app():
    app = web.Application()

    # app.on_startup.append(UserView.startup_1)
    # app.cleanup_ctx.append(UserView.cleanup_ctx_2)
    # app.on_startup.append(UserView.startup_3)

    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))

    app.router.add_view('/users', UserView)
    return app


if __name__ == '__main__':
    web.run_app(make_app(), port=7070)