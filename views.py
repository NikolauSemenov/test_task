from aiohttp import web
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

import json
import datetime

from models import UsersClass, RulesClass
from logger_app import LoggingMain

logger = LoggingMain().get_logging('Test_task')

engine = create_engine('postgresql+psycopg2://admin:admin@localhost/test_db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()


class UserView:

    def __init__(self):
        self.is_verified = False
        self.root = False

    async def authorization(self, request):
        """
        Функция авторизации.
        """
        login = request.match_info.get('name', False)
        password = request.match_info.get('password', False)
        if login and password:
            query = session.query(UsersClass, RulesClass).filter_by(login=login).first()
            if query:
                if query[0].password == password:
                    self.is_verified = True
                    admin_flag = query[1]
                    if bool(admin_flag):
                        self.root = True
                    return web.Response(text=json.dumps('Authorized'), status=200)

        self.is_verified = False
        logger.warning("Введены неправильные данные для авторизации")
        return web.Response(text=json.dumps('Forbidden'), status=403)

    async def post(self, request):
        """
        Данная функция добавляет нового пользователя.
        """
        if not self.is_verified and not self.root:
            return web.Response(text='Forbidden')

        name = request.match_info.get('name', False)
        last_name = request.match_info.get('last_name', False)
        login = request.match_info.get('login', False)
        password = request.match_info.get('password', False)
        date = request.match_info.get('date', False)
        admin_flag = bool(request.match_info.get('admin_flag', False))

        birthday = datetime.datetime.strptime(date, '%Y-%m-%d')

        try:
            users = UsersClass(name=name,
                               last_name=last_name,
                               login=login,
                               password=password,
                               birthday=birthday)
            session.add(users)
            session.flush()

            query = session.query(UsersClass).filter_by(login=login).first()

            rules = RulesClass(block=False, admin=admin_flag, only_read=False if admin_flag is True else True, user_id=query.id)

            session.add(rules)
            session.commit()
        except exc.IntegrityError:
            logger.error("Повторения зачения")
            return web.Response(text='Forbidden')

        except exc.PendingRollbackError:
            logger.error("Нарушено уникальность значений")
            return web.Response(text='Forbidden')

        return web.Response(text='Успешно создан')

    async def delete(self, request):
        """
        Данная функция удаляет пользователя из бд по логину.
        """
        login = request.match_info.get('login', False)
        if login and self.is_verified and self.root:
            query = session.query(UsersClass, RulesClass).filter_by(login=login).first()
            if query is not None:
                session.delete(query[1])
                session.delete(query[0])

                session.commit()
                return web.Response(text='Пользователь успешно удален')

        return web.Response(text='Forbidden')

    async def update(self, request):
        """
        Данная функция обновляет имя и фамилию пользователя
        """
        login = request.match_info.get('login', False)
        name = request.match_info.get('name', False)
        last_name = request.match_info.get('last_name', False)

        if name and self.is_verified and self.root:
            query = session.query(UsersClass).filter(UsersClass.login == login).one()
            query.name = name
            query.last_name = last_name

            session.commit()
            return web.Response(text='Пользователь успешно обновлен')
        return web.Response(text='Forbidden')

    async def get_user(self, request):
        """
        Возвращает пользователя по login
        """
        login = request.match_info.get('login', False)
        if login:
            query = session.query(UsersClass).filter_by(login=login).first()
            return web.Response(text=f"{query}")

        return web.Response(text='Forbidden')


classUser = UserView()
app = web.Application()

app.add_routes([web.post('/{name}&{password}', classUser.authorization),
                web.put('/{name}&{last_name}&{login}&{password}&{date}&{admin_flag}', classUser.post),
                web.delete('/{login}', classUser.delete),
                web.patch('/{login}&{name}&{last_name}', classUser.update),
                web.get('/{login}', classUser.get_user)])

if __name__ == '__main__':
    web.run_app(app)