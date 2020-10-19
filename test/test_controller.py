import asyncio

import pytest
import quart
import quart.flask_patch
import quart.flask_patch
import quart.testing
import quart.testing

import controller
from controller import app as app_for_testing


@pytest.fixture
def client():
    app_for_testing.config['TESTING'] = True

    yield app_for_testing.test_client()


@pytest.mark.asyncio
async def test_api(client):
    response: quart.wrappers.Response

    response = await client.get('/api/')
    assert response.status_code == 200

    data = await response.get_data()
    assert data


@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_run_area(client):
    response: quart.wrappers.Response

    controller.initialize_config()
    controller._init_strips()
    controller._init_areas()

    response = await client.get('/run/default/fire/')
    print(await response.get_data())
    assert response.status_code == 200

    await asyncio.sleep(1)
    await controller.available_areas['default'].stop()
    await asyncio.sleep(1)
