from api import app

from hypercorn.asyncio import serve
from hypercorn.config import Config
from typing import Any, Coroutine
from postDB import Model
from quart import Quart
import logging
import asyncio
import asyncpg
import click
import sys
import os


logging.basicConfig(level=logging.DEBUG)


try:
    import uvloop  # noqa
except ModuleNotFoundError:
    loop = asyncio.new_event_loop()
else:
    loop = uvloop.new_event_loop()

asyncio.set_event_loop(loop)

app: Quart
ENV_FILE = "./local.env"
ENV = dict(
    SECRET_KEY=None, DB_URI=None, DISCORD_CLIENT_ID=None, DISCORD_CLIENT_SECRET=None
)


try:
    with open(ENV_FILE) as f:
        env_file = {
            key.strip(): arg.strip()
            for (key, arg) in [
                line.strip().split("=") for line in f.readlines() if line.strip()
            ]
        }
except FileNotFoundError:
    env_file = {}


for key in ENV.keys():
    try:
        ENV[key] = os.environ[key]
    except KeyError:
        try:
            ENV[key] = env_file[key]
            os.environ[key] = ENV[key]
        except KeyError:
            sys.stderr.write(f"Found no `{key}` var in env, exiting..."), exit(1)

app.config.from_mapping(mapping=ENV)


def run_async(coro: Coroutine) -> Any:
    """
    Used to run coroutines outside any coroutine.

    :param coro:    The coroutine to run.
    :returns:       Whatever the coroutine returned.
    """
    return loop.run_until_complete(coro)


async def prepare_postgres(retries: int = 5, interval: float = 10.0) -> bool:
    """
    Prepare the postgres database connection.

    :param int retries:     Included to fix issue with docker starting API before DB is finished starting.
    :param float interval:  Interval of which to wait for next retry.
    """
    log = logging.getLogger("DB")
    db_name = ENV["DB_URI"].split("/")[-1]
    log.info('[i] Attempting to connect to DB "%s"' % db_name)
    for i in range(1, retries + 1):
        try:
            await Model.create_pool(
                uri=ENV["DB_URI"],
                max_con=10,  # We might want to increase this number in the future.
                loop=loop,
            )

        except asyncpg.InvalidPasswordError as e:
            log.error("[!] %s" % str(e))
            return False

        except (ConnectionRefusedError, ):
            log.warning(
                "[!] Failed attempt #%s/%s, trying again in %ss"
                % (i, retries - i, interval)
            )

            if i == retries:
                log.error("[!] Failed final connection attempt, exiting.")
                return False

            await asyncio.sleep(interval)

    log.info('[✔] Connected to database "%s"' % db_name)
    return True


async def safe_create_tables(verbose: bool = False) -> None:
    """
    Safely create all tables using the specified order in `~/api/models/__init__.py`.

    :param verbose:     Whether or not to print the postgres statements being executed.
    """
    log = logging.getLogger("DB")
    from api.models import models_ordered

    log.info("Attempting to create %s tables." % len(models_ordered))

    for model in models_ordered:
        await model.create_table(verbose=verbose)
        log.info("Created table %s" % type(model).__tablename__)


@app.cli.command(name="initdb")
@click.option("--verbose", default=False, is_flag=True)
def _initdb(verbose: bool):
    """
    Creates all tables defined in the app.

    :param verbose:     Print SQL statements when creating models?
    """
    if not run_async(prepare_postgres(retries=6, interval=10.0)):
        exit(1)  # Connecting to our postgres server failed.

    run_async(safe_create_tables(verbose=verbose))


@app.cli.command()
@click.option("--verbose", default=False, is_flag=True)
def dropdb(verbose: bool):
    """
    Drops all tables defined in the app.

    :param verbose:     Print SQL statements when dropping models?
    """
    if not run_async(prepare_postgres(retries=6, interval=10.0)):
        exit(1)  # Connecting to our postgres server failed.

    log = logging.getLogger("DB")

    for model in Model.all_models():
        run_async(model.drop_table(verbose=verbose))
        log.info("Dropped table %s" % type(model).__tablename__)


@app.cli.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default="5000")
@click.option("--initdb", default=False, is_flag=True)
@click.option("--verbose", default=False, is_flag=True)
def runserver(host: str, port: str, initdb: bool, verbose: bool):
    """
    Run the Quart app.

    :param host:        Host to run it on.
    :param port:        Port to run it on.
    :param initdb:      Create models before running API?
    :param verbose:     Print SQL statements when creating models?
    """
    if not run_async(prepare_postgres(retries=6, interval=10.0)):
        exit(1)  # Connecting to our postgres server failed.

    if initdb:
        run_async(safe_create_tables(verbose=verbose))

    config = Config()
    config.bind = [host + ":" + port]
    run_async(serve(app, config))


if __name__ == "__main__":
    app.cli()
