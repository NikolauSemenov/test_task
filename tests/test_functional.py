import pytest
from pytest import fixture

from data_for_test import test_data, fake, cli, migrated_postgres


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
