from aiohttp import web
from pytest import fixture
from sqlalchemy_utils import create_database, drop_database
from faker import Faker

from views import connect_db, UserView
from config import read_config

fake = Faker()

test_data = {"name": fake.first_name_male(),
             "last_name": fake.last_name(),
             "login": fake.suffix(),
             "password": fake.bban(),
             "birthday": fake.date()}


@fixture(scope='session')
def migrated_postgres():
    config = get_config()['app']
    pg_url = f"postgresql://{config['user']}:{config['password']}@{config['host']}/{config['namedb']}_test"
    create_database(url=pg_url)
    yield
    drop_database(pg_url)


def get_config():
    config = read_config()
    return config


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_view('/users', UserView)
    app.cleanup_ctx.append(connect_db)
    return app


@fixture()
def cli(migrated_postgres, aiohttp_client, loop):
    app = create_app()
    return loop.run_until_complete(aiohttp_client(app))


async def test_get_request(cli):
    resp = await cli.get('/users')
    assert resp.status == 200


async def test_post_request(cli):
    resp = await cli.post('/users', json=test_data)
    assert resp.status == 201


async def test_put_request(cli):
    resp = await cli.put('/users', json={"login": test_data['login'],
                                         "name": test_data['name'],
                                         "last_name": test_data['last_name']})
    assert resp.status == 200


async def test_delete_request(cli):
    resp = await cli.delete('/users', json={"login": test_data['login']})
    assert resp.status == 204
