import json
import os

import pytest
from aiohttp import web
from pytest import fixture
from sqlalchemy_utils import create_database, drop_database
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

from views import make_app
from config import read_config


fake = Faker("ru_RU")

test_data = {"name": fake.first_name_male(),
             "last_name": fake.last_name(),
             "login": fake.suffix(),
             "password": fake.bban(),
             "birthday": fake.date()}


def get_config():
    return read_config()


def save_url(url) -> None:
    with open("path.json", "w", encoding='utf-8') as config_file:
        json.dump({"path": url}, config_file, indent=2, ensure_ascii=False, separators=(',', ': '))


async def connect_db(app: web.Application):
    config_db = get_config()['app']
    url = f"postgresql+asyncpg://{config_db['user']}:{config_db['password']}@{config_db['host']}/{config_db['namedb']}_test"
    engine = create_async_engine(url, echo=False)
    session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    session_db = session()
    app["session_db"] = session_db
    yield
    await session_db.close()


@fixture(scope='session')
def migrated_postgres():
    config_my = get_config()['app']
    pg_url = f"postgresql://{config_my['user']}:{config_my['password']}@{config_my['host']}/{config_my['namedb']}_test"
    create_database(url=pg_url)
    save_url(pg_url)

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    yield
    drop_database(pg_url)
    os.remove("path.json")


def create_app() -> web.Application:
    app = make_app()
    app.cleanup_ctx.append(connect_db)
    return app


@fixture()
def cli(migrated_postgres, aiohttp_client, loop):
    app = create_app()
    return loop.run_until_complete(aiohttp_client(app))


async def test_post_request(cli):
    resp = await cli.post('/users', json=test_data)
    assert resp.status == 201


async def test_get_request(cli):
    resp = await cli.get('/users')
    assert resp.status == 200


async def test_post_request_duplicate(cli):
    resp = await cli.post('/users', json=test_data)
    assert resp.status == 400


async def test_post_request_error_input_data(cli):
    resp = await cli.post('/users', json=fake.json())
    assert resp.status == 422


@pytest.mark.parametrize("fake_name", [(fake.name()[:4])])
async def test_post_request_not_valid_name(cli, fake_name):
    test_data['name'] = fake_name
    resp = await cli.post('/users', json=test_data)
    assert resp.status == 422


async def test_put_request(cli):
    resp = await cli.put('/users', json={"login": test_data['login'],
                                         "name": test_data['name'],
                                         "last_name": test_data['last_name']})
    assert resp.status == 200


async def test_delete_request(cli):
    resp = await cli.delete('/users', json={"login": test_data['login']})
    assert resp.status == 204
