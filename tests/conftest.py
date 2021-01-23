from api import app as quart_app
from api.models import User
from launch import load_env, prepare_postgres, safe_create_tables, delete_tables

from quart.testing import QuartClient
from postDB import Model
import pytest
import asyncio
import datetime
import jwt
import os


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def app(event_loop) -> QuartClient:
    return quart_app.test_client()


@pytest.fixture(scope="session")
async def auth_app(event_loop, db) -> QuartClient:
    auth_client = quart_app.test_client()
    user = await User.create(1, "test", "0000", type="APP")
    auth_client.token = jwt.encode(
        {"uid": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1), "iat": datetime.datetime.utcnow()},
        key=os.environ["SECRET_KEY"],
    )
    return auth_client


@pytest.fixture(scope="session")
async def db(event_loop) -> bool:
    env = load_env("./local.env", ("TEST_DB_URI",))
    assert await prepare_postgres(db_uri=env["TEST_DB_URI"], loop=event_loop)
    await safe_create_tables()
    yield Model.pool
    await delete_tables()


def pytest_addoption(parser):
    parser.addoption(
        "--no-db",
        action="store_true",
        default=False,
        help="don't run tests that require a database set up",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "db: mark test as needing an database to run")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--no-db"):
        # --no-db not given in cli: do not skip tests that require database
        return

    skip_db = pytest.mark.skip(reason="need --no-db option removed to run")
    for item in items:
        if "db" in item.keywords:
            item.add_marker(skip_db)
