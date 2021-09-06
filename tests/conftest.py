import jwt
import config
import pytest
import asyncio

from postDB import Model
from httpx import AsyncClient

from api.models import User
from launch import prepare_postgres, safe_create_tables, delete_tables


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def app(event_loop: asyncio.AbstractEventLoop) -> AsyncClient:
    from api import app

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        await app.router.startup()
        yield client
        await app.router.shutdown()


@pytest.fixture(scope="session")
async def db(event_loop) -> bool:
    assert await prepare_postgres(db_uri=config.test_postgres_uri(), loop=event_loop)
    await safe_create_tables()
    yield Model.pool
    await delete_tables()


@pytest.fixture(scope="function")
async def user(db):
    yield await User.create(0, "Test", "0001")
    await db.execute("""DELETE FROM users WHERE username = 'Test'""")


@pytest.fixture(scope="function")
async def token(user, db):
    yield jwt.encode(
        {"uid": user.id},
        key=config.secret_key(),
    )


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
