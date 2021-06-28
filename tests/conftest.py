from launch import prepare_postgres, safe_create_tables, delete_tables
from api import config

from fastapi.testclient import TestClient
from postDB import Model
import asyncio
import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def app(event_loop) -> TestClient:
    from api import app

    return TestClient(app)


@pytest.fixture(scope="session")
async def db(event_loop) -> bool:
    config.load_env("./local.env")
    assert await prepare_postgres(db_uri=config.TEST_DB_URI, loop=event_loop)
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
