from aiohttp.test_utils import AioHTTPTestCase
from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from requests_db import get_users
from views import UserView, connect_db


async def get_session():
    engine = create_async_engine('postgresql+asyncpg://postgres:12345@localhost/test', echo=False)
    session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    return session()


async def test_get_request(request, test_client, loop):

    session_db = get_session()

    class_user = UserView(request)
    get_ = await class_user.get()
    # get_ = await get_users(session_db)

    app = web.Application(loop=loop)
    app.router.add_route("GET", "/", get_)
    app.cleanup_ctx.append(connect_db)

    client = await test_client(app)

    resp = await client.get('/')
    assert resp.status == 200
