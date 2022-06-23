import asyncio
import asyncpg 
import pytest

from tortoise.contrib.test import finalizer, initializer
from tortoise.exceptions import DBConnectionError
from tortoise import Tortoise
from asyncpg.exceptions import DuplicateDatabaseError
from urllib.parse import urlparse
from aerich import Command

from util.tortoise_config import AERICH_CONFIG
from config import CONFIG


@pytest.fixture(scope="function", autouse=True)
async def database(tortoise_config):
    await Tortoise.init(tortoise_config)
    yield
    for model in Tortoise.apps.get('models').values():
        await model.all().delete()
    await Tortoise.close_connections()


@pytest.fixture(scope="session")
async def tortoise_config(test_db_url):
    config = AERICH_CONFIG
    print(config["connections"]["default"])
    config["connections"]["default"] = test_db_url
    return config


@pytest.fixture(scope="session")
async def test_db_url(worker_id):
    if worker_id == "master":
        return CONFIG.TEST_DATABSE_URL
    else:
        return CONFIG.TEST_DATABSE_URL + f"_{worker_id}"


async def delete_db(tortoise_config):
    await Tortoise.init(tortoise_config) #open connection
    rules_connection = Tortoise.get_connection('default')
    await rules_connection.close()
    await rules_connection.db_delete()
    await Tortoise.close_connections()


async def create_db(test_db_url):
    con_url = urlparse(test_db_url)
    username = con_url.username
    password = con_url.password
    hostname = con_url.hostname
    database_name = con_url.path[1:]
    port = con_url.port
    sys_conn = await asyncpg.connect(
        user = username,
        password = password,
        host = hostname,
        port = port,
        database="postgres",
        # max_inactive_connection_lifetime=100
    )

    name = test_db_url.split("/")[-1]
    try:
        await sys_conn.execute(
            f'CREATE DATABASE "{name}" OWNER "{username}"'
        )
    except DuplicateDatabaseError:
        pass
    await sys_conn.close()


@pytest.fixture(scope="session", autouse=True)
async def init_tortoise(test_db_url, tortoise_config):
    try:
        await delete_db(tortoise_config)
    except DBConnectionError:
        pass
    
    await create_db(test_db_url)

    await Tortoise.init(tortoise_config)
    command = Command(
        tortoise_config=tortoise_config, 
        app='models',
    )
    await command.init()
    await command.upgrade()
    await Tortoise.close_connections()

    yield

    # await Command.downgrade()
    await delete_db(tortoise_config)


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()