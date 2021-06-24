from typing import Optional

from multidict import MultiDictProxy
from aiohttp import web
from marshmallow.exceptions import ValidationError
from marshmallow import Schema
from sqlalchemy import exc
from sqlalchemy.orm import Session

from models import UsersClass,RulesClass
from logger_app import LoggingMain

logger = LoggingMain().get_logging('Test_task')


def load_data(data: MultiDictProxy, schema: Schema) -> dict:
    try:
        return schema.load(data)
    except ValidationError as e:
        logger.error(f"{e}")
        raise web.HTTPUnprocessableEntity(text=str(e.messages))


def get_users(session_db: Session):
    with session_db as session:
        return session.query(UsersClass).all()


def save_users(session_db: Session, data: dict) -> None:
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


def delete_user(session_db: Session, data: dict) -> Optional[bool]:
    with session_db as session:
        with session.begin():
            try:
                query = session.query(UsersClass, RulesClass).filter_by(login=data['login']).first()
                if query is not None:
                    session.delete(query[0])
                    session.delete(query[1])
            except:
                # TODO указать явные исключения
                session.rollback()
            else:
                session.commit()
                return True


def update_user(session_db: Session, data: dict) -> None:
    with session_db as session:
        with session.begin():
            try:
                query = session.query(UsersClass).filter(UsersClass.login == data['login']).one()
                query.name = data['name']
                query.last_name = data['last_name']
            except:
                # TODO указать явные исключения
                session.rollback()
                raise web.HTTPError()
            else:
                session.commit()