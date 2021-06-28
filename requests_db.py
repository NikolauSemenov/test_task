from typing import Optional

from aiohttp import web
from sqlalchemy import exc, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from logger_app import LoggingMain
from models import UsersClass, RulesClass

logger = LoggingMain().get_logging('Test_task')


async def get_users(session_db: AsyncSession) -> list:
    result = await session_db.execute(select(UsersClass))
    return result.scalars().all()


async def save_users(session_db: AsyncSession, data: dict) -> None:
    async with session_db as session:
        async with session.begin():
            try:
                user_add = UsersClass(name=data['name'],
                                      last_name=data['last_name'],
                                      password=data['password'],
                                      birthday=data['birthday'],
                                      login=data['login']
                )
                session.add(user_add)
                await session.flush()

                select_user = select(UsersClass.id).filter_by(login=data['login'])
                admin_flag = data['admin_flag']
                rules = RulesClass(
                    block=False,
                    admin=admin_flag,
                    only_read=admin_flag,
                    user_id=select_user
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
            else:
                await session.commit()


async def delete_user(session_db: AsyncSession, data: dict) -> Optional[bool]:
    async with session_db as session:
        async with session.begin():
            try:
                user = await session.execute(select(UsersClass.id).filter_by(login=data['login']))
                user_id = user.scalars().all()[0]

                await session.execute(delete(RulesClass).filter_by(user_id=user_id))
                await session.execute(delete(UsersClass).filter_by(login=data['login']))

            except Exception as EXC:
                logger.error(EXC)
                session.rollback()
                raise web.HTTPBadRequest()
            except exc.InvalidRequestError as e:
                logger.error(e)
                session.rollback()
                raise web.HTTPBadRequest()
            else:
                await session.commit()
                return True


async def update_user(session_db: AsyncSession, data: dict) -> None:
    async with session_db as session:
        async with session.begin():
            try:
                await session.execute(update(UsersClass)
                                      .filter_by(login=data['login'])
                                      .values(name=data['name'])
                                      .values(last_name=data['last_name']))
            except Exception as EXC:
                logger.error(EXC)
                session.rollback()
                raise web.HTTPError()
            else:
                await session.commit()
