from typing import Optional

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from logger_app import LoggingMain
from models import UsersClass, RulesClass

logger = LoggingMain().get_logging('Test_task')


async def get_users(session_db: AsyncSession) -> list:
    result = await session_db.execute(select(UsersClass))
    return result.scalars().all()


async def save_users(session: AsyncSession, data: dict) -> None:
    user_add = UsersClass(
        name=data['name'],
        last_name=data['last_name'],
        password=data['password'],
        birthday=data['birthday'],
        login=data['login']
    )
    session.add(user_add)
    await session.flush()
    rules = await add_rules_user(data, user_add.id)
    session.add(rules)


async def add_rules_user(data: dict, user_id: int) -> RulesClass:
    admin_flag = data['admin_flag']
    rules = RulesClass(
        block=False,
        admin=admin_flag,
        only_read=admin_flag,
        user_id=user_id)
    return rules


async def delete_user(session: AsyncSession, data: dict) -> Optional[bool]:
    user = await session.execute(select(UsersClass.id).filter_by(login=data['login']))
    user_id = user.scalars().all()[0]

    await session.execute(delete(RulesClass).filter_by(user_id=user_id))
    await session.execute(delete(UsersClass).filter_by(login=data['login']))
    return True


async def update_user(session: AsyncSession, data: dict) -> None:
    await session.execute(update(UsersClass)
                          .filter_by(login=data['login'])
                          .values(name=data['name'])
                          .values(last_name=data['last_name']))
