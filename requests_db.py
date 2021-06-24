from typing import Optional

from aiohttp import web
from sqlalchemy import exc
from sqlalchemy.orm import Session

from logger_app import LoggingMain
from models import UsersClass, RulesClass

logger = LoggingMain().get_logging('Test_task')


async def get_users(session_db: Session) -> list:
    with session_db as session:
        return session.query(UsersClass).all()


async def save_users(session_db: Session, data: dict) -> None:
    with session_db as session:
        with session.begin():
            try:
                users = UsersClass(
                    name=data['name'],
                    last_name=data['last_name'],
                    login=data['login'],
                    password=data['password'],
                    birthday=data['birthday']
                )
                session.add(users)
                session.flush()

                query = session.query(UsersClass).filter_by(login=data['login']).first()
                admin_flag = data['admin_flag']
                rules = RulesClass(
                    block=False,
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


async def delete_user(session_db: Session, data: dict) -> Optional[bool]:
    with session_db as session:
        with session.begin():
            try:
                query = (
                    session.query(UsersClass, RulesClass)
                    .filter_by(login=data['login'])
                    .first()
                )
                # query = (
                #     session.query(UsersClass)
                #     .join(RulesClass, RulesClass.user_id == UsersClass.id)
                #     .filter(UsersClass.login == data['login'])
                # )
                if query is not None:
                    session.delete(query[0])
                    session.delete(query[1])
            except Exception as EXC:
                logger.error(EXC)
                session.rollback()
            else:
                session.commit()
                return True


async def update_user(session_db: Session, data: dict) -> None:
    with session_db as session:
        with session.begin():
            try:
                query = (
                    session.query(UsersClass)
                    .filter(UsersClass.login == data['login'])
                    .one()
                )
                query.name = data['name']
                query.last_name = data['last_name']
            except Exception as EXC:
                logger.error(EXC)
                session.rollback()
                raise web.HTTPError()
            else:
                session.commit()
