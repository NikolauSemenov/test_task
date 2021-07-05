from contextlib import asynccontextmanager
from typing import Callable, Awaitable
import async_timeout

from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from aiohttp_apispec import (validation_middleware,
                             setup_aiohttp_apispec,
                             request_schema,
                             docs,
                             response_schema)
from aiohttp.web_routedef import StreamResponse

from base import BaseView
from config import read_config
from serelizator import UserSchema, UpdateSchema, DeleteSchema, UsersList


class UserView(BaseView):

    @docs(
        tags=["users"],
        summary="Вернуть список пользователей",
        description="Возвращает список всех пользователей из базы данных",
        responses={
            404: {"description": "Not Found"},
            500: {"description": "Server error"},
        }
    )
    @response_schema(UsersList(), 200, description="Ok. Users list")
    async def get(self) -> web.Response:
        """
        Данная функция возвращает пользователей
        """
        resp = await self.db.get_users(self.session)
        if not resp:
            raise web.HTTPNotFound()
        return web.json_response(data=self.dump({'users': resp}, UsersList()))

    @docs(
        tags=["users"],
        summary="Создание нового пользователя",
        description="Добавление нового пользователя в базу данных",
        responses={
            201: {"description": "Ok. User created"},
            401: {"description": "Unauthorized"},
            422: {"description": "Validation error"},
            500: {"description": "Server error"},
        }
    )
    @request_schema(UserSchema())
    async def post(self) -> web.Response:
        """
        Данная функция добавляет нового пользователя.
        """
        input_data = self.request['data']
        await self.db.save_users(self.session, input_data)
        return web.HTTPCreated()

    @docs(
        tags=["users"],
        summary="Удаление пользователя",
        description="Производит удаление пользователя по логину из базы данных",
        responses={
            204: {"description": "Ok. User delete"},
            401: {"description": "Unauthorized"},
            422: {"description": "Validation error"},
            500: {"description": "Server error"},
        }
    )
    @request_schema(DeleteSchema)
    async def delete(self) -> web.Response:
        """
        Данная функция удаляет пользователя из бд по логину.
        """
        input_data = self.request['data']
        if await self.db.delete_user(self.session, input_data):
            return web.HTTPNoContent()
        raise web.HTTPBadRequest()

    @docs(
        tags=["users"],
        summary="Изменение данных пользователя",
        description="Позволяет изменять имя и фамилию пользователя",
        responses={
            200: {"description": "Ok. User update"},
            401: {"description": "Unauthorized"},
            422: {"description": "Validation error"},
            500: {"description": "Server error"},
        }
    )
    @request_schema(UpdateSchema)
    @response_schema(DeleteSchema(), 200)
    async def put(self) -> web.Response:
        """
        Данная функция обновляет имя и фамилию пользователя
        """
        input_data = self.request['data']
        await self.db.update_user(self.session, input_data)
        return web.HTTPOk()


def get_config():
    config = read_config()
    return config


Handler = Callable[[web.Request], Awaitable[StreamResponse]]


@web.middleware
async def exceptions(request: web.Request, handler: Handler) -> StreamResponse:
    try:
        return await handler(request)
    except web.HTTPException:
        raise
    except Exception as exc:
        raise web.HTTPInternalServerError(text=f"{exc}")


@asynccontextmanager
async def atomic(request: web.Request):
    async with request.app["session_db"] as session:
        async with session.begin():
            try:
                yield session
                await session.commit()
            except Exception as exc:
                await session.rollback()
                raise web.HTTPBadRequest(text=f"{exc}")


@web.middleware
async def transaction(request: web.Request, handler: Handler) -> StreamResponse:
    if request.method in ["GET", "OPTION", "HEAD"]:
        request.session = request["session"] = request.app["session_db"]
        return await handler(request)
    else:
        async with atomic(request) as session:
            request.session = request["session"] = session
            return await handler(request)


async def connect_db(app: web.Application):
    config = get_config()['app']
    async with async_timeout.timeout(5):
        engine = create_async_engine(f"postgresql+asyncpg://{config['user']}:{config['password']}@{config['host']}/{config['namedb']}", echo=False)
        session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
        session_db = session()
        app["session_db"] = session_db
    yield
    await session_db.close()


def make_app() -> web.Application:
    middlewares = [exceptions, validation_middleware, transaction]

    app = web.Application(middlewares=middlewares)
    app.router.add_view('/users', UserView)
    app.cleanup_ctx.append(connect_db)
    setup_aiohttp_apispec(app, swagger_path="/docs")
    return app


if __name__ == '__main__':
    web.run_app(make_app())