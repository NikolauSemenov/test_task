from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from multidict import MultiDictProxy
from aiohttp import web
from marshmallow.exceptions import ValidationError
from marshmallow import Schema

from logger_app import LoggingMain

Base = declarative_base()
engine = create_engine('sqlite:///test.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

logger = LoggingMain().get_logging('Test_task')


class UsersClass(Base):
    """
    Класс описывающий сущность пользователей
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    login = Column(String(64), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    birthday = Column(DateTime(), nullable=False)
    dl = relationship('RulesClass', backref='users', uselist=False)

    def __init__(self, name: str, last_name: str, login: str, password: str, birthday: str):
        self.name = name
        self.last_name = last_name
        self.login = login
        self.birthday = birthday
        self.password = password

    def __repr__(self):
        return '<User %r>' %(self.name)


class RulesClass(Base):
    """
    Класс описывает права доступа для пользователей.
    """
    __tablename__ = 'rules'

    id = Column(Integer, primary_key=True)
    block = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    only_read = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, block: bool, admin: bool, only_read: bool, user_id: int):
        self.block = block
        self.admin = admin
        self.only_read = only_read
        self.user_id = user_id

    def __repr__(self):
        return '%r' %(self.admin)


def load_data(data: MultiDictProxy, schema: Schema) -> dict:
    """
    Данная функция проверяет входные данные
    """
    try:
        return schema.load(data)
    except ValidationError as e:
        logger.error(f"{e}")
        raise web.HTTPUnprocessableEntity(text=str(e.messages))


def get_users():
    return session.query(UsersClass).all()


def save_users(session_db: Session, data: MultiDictProxy) -> None:
    with session_db as session:
        with session.begin():
            try:
                users = UsersClass(name=data['name'],
                                   last_name=data['last_name'],
                                   login=data['login'],
                                   password=data['password'],
                                   birthday=data['birthday']
                            )
                session.add(users)
                session.flush()

                query = session.query(UsersClass).filter_by(login=data['login']).first()
                admin_flag = data['admin_flag']
                rules = RulesClass(block=False,
                                   admin=admin_flag,
                                   only_read=admin_flag,
                                   user_id=query.id
                )
                session.add(rules)
            except exc.IntegrityError as e:
                session.rollback()
                logger.error(f"{e}")
                raise web.HTTPBadRequest()

            except exc.PendingRollbackError as e:
                session.rollback()
                logger.error(f"{e}")
                raise web.HTTPBadRequest()

            except KeyError as e:
                session.rollback()
                logger.error(f"{e}")
                raise web.HTTPBadRequest()
            else:
                session.commit()


def delete_user(session_db: Session, data: MultiDictProxy) -> Boolean:
    with session_db as session:
        with session.begin():
            try:
                query = session.query(UsersClass, RulesClass).filter_by(login=data['login']).first()
                if query is not None:
                    session.delete(query[0])
                    session.delete(query[1])
            except:
                session.rollback()
                return False
            else:
                session.commit()
                return True


def update_user(session_db: Session, data: MultiDictProxy) -> None:
    with session_db as session:
        with session.begin():
            try:
                query = session.query(UsersClass).filter(UsersClass.login == data['login']).one()
                query.name = data['name']
                query.last_name = data['last_name']
            except:
                session.rollback()
                raise web.HTTPError()
            else:
                session.commit()