import json
import datetime

from aiohttp import web
from aiohttp.web import View

from sqlalchemy import exc
from marshmallow.exceptions import ValidationError

from connect_db import DatabaseTransaction
from models import UsersClass, RulesClass
from logger_app import LoggingMain
from serelizator import UserSchema

logger = LoggingMain().get_logging('Test_task')


class UserView(View):

    def get_connect_db(self):
        """
        Осуществляется подключение к бд
        """
        try:
            return DatabaseTransaction('test.db')
        except:
            return False

    async def validate_data(self, data):
        """
        Данная функция проверяет входные данные
        """
        try:
            input_data = UserSchema.load(data)
        except ValidationError:
            return False
        return input_data

    async def get(self) -> web.Response:
        """
        Данная функция возвращает пользователей
        """
        connect_db = self.get_connect_db()
        with connect_db as db_connect:
            with db_connect as cursor:
                query = cursor.query(UsersClass).all()
                return web.Response(text=f"{query}")

    async def post(self) -> web.Response:
        """
        Данная функция добавляет нового пользователя.
        """
        # request = await get_response(self.request)
        input_data = self.request.query
        # input_data = self.validate_data(request)
        connect_db = self.get_connect_db()

        if input_data:
            birthday = datetime.datetime.strptime(input_data.get('birthday'), '%Y-%m-%d')

            try:
                users = UsersClass(name=input_data.get('name'),
                                   last_name=input_data.get('last_name'),
                                   login=input_data.get('login'),
                                   password=input_data.get('password'),
                                   birthday=birthday)

                with connect_db as db_connect:
                    with db_connect as session:
                        session.add(users)
                        session.flush()

                        query = session.query(UsersClass).filter_by(login=input_data.get('login')).first()
                        admin_flag = input_data.get('admin_flag')
                        rules = RulesClass(block=False,
                                           admin=admin_flag,
                                           only_read=False if admin_flag is True else True,
                                           user_id=query.id)

                        session.add(rules)
                        session.commit()

            except exc.IntegrityError as e:
                logger.error(f"{e}")
                raise web.HTTPForbidden()

            except exc.PendingRollbackError as e:
                logger.error(f"{e}")
                raise web.HTTPForbidden()

            return web.Response(text='Пользователь успешно создан')

    async def delete(self) -> web.Response:
        """
        Данная функция удаляет пользователя из бд по логину.
        """
        # input_data = self.validate_data(request)
        input_data = self.request.query
        connect_db = self.get_connect_db()

        if input_data:
            with connect_db as db_connect:
                with db_connect as session:
                    query = session.query(UsersClass, RulesClass).filter_by(login=input_data.get('login')).first()
                    if query is not None:
                        session.delete(query[1])
                        session.delete(query[0])

                        session.commit()
                        return web.Response(text='Пользователь успешно удален')

        raise web.HTTPForbidden()

    async def update(self) -> web.Response:
        """
        Данная функция обновляет имя и фамилию пользователя
        """
        # input_data = self.validate_data(request)
        input_data = self.request.query

        connect_db = self.get_connect_db()

        if input_data:
            with connect_db as db_connect:
                with db_connect as session:
                    query = session.query(UsersClass).filter(UsersClass.login == input_data.get('login')).one()
                    query.name = input_data.get('name')
                    query.last_name = input_data.get('last_name')

                    return web.Response(text='Пользователь успешно обновлен')
        raise web.HTTPForbidden()


app = web.Application()
app.router.add_view('/users', UserView)

if __name__ == '__main__':
    web.run_app(app, port=8080)