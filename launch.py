from api import app

from typing import Any, Coroutine, Iterable
from hypercorn.asyncio import serve
from hypercorn.config import Config
from postDB import Model
import logging
import asyncio
import asyncpg
import click
import sys
import os


logging.basicConfig(level=logging.INFO)


try:
    import uvloop  # noqa f401
except ModuleNotFoundError:
    loop = asyncio.new_event_loop()
else:
    loop = uvloop.new_event_loop()

asyncio.set_event_loop(loop)


def load_env(fp: str, args: Iterable[str], exit_on_missing: bool = True) -> dict:
    """
    Load all env values from `args`.

    :param fp:              Local file to load from
    :param args:            Arguments to load
    :param exit_on_missing: Exit on missing env values?
    """
    if not (env := {arg: None for arg in args}):
        return env  # Return if `args` is empty.

    try:
        with open(fp) as f:
            env_file = {
                key.strip(): arg.strip()
                for (key, arg) in [
                    line.strip().split("=") for line in f.readlines() if line.strip()
                ]
            }
    except FileNotFoundError:
        env_file = {}

    for key in args:
        try:
            env[key] = os.environ[key]
        except KeyError:
            try:
                env[key] = env_file[key]
                os.environ[key] = env[key]
            except KeyError:
                if exit_on_missing:
                    sys.stderr.write(
                        "Found no `%s` var in env, exiting..." % key
                    ), exit(1)

                sys.stderr.write(
                    "Found no `%s` var in env, setting as empty string." % key
                )
                env[key] = ""
                os.environ[key] = ""

    return env


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

        except (ConnectionRefusedError,):
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
        log.info("Created table %s" % model.__tablename__)


@app.cli.command(name="initdb")
@click.option("-v", "--verbose", default=False, is_flag=True)
def _initdb(verbose: bool):
    """
    Creates all tables defined in the app.

    :param verbose:     Print SQL statements when creating models?
    """
    if not run_async(prepare_postgres(retries=6, interval=10.0)):
        exit(1)  # Connecting to our postgres server failed.

    run_async(safe_create_tables(verbose=verbose))


@app.cli.command()
@click.option("-v", "--verbose", default=False, is_flag=True)
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
        log.info("Dropped table %s" % model.__tablename__)


@app.cli.command()
@click.option("-h", "--host", default="127.0.0.1")
@click.option("-p", "--port", default="5000")
@click.option("-d", "--debug", default=False, is_flag=True)
@click.option("-i", "--initdb", default=False, is_flag=True)
@click.option("-v", "--verbose", default=False, is_flag=True)
def runserver(host: str, port: str, debug: bool, initdb: bool, verbose: bool):
    """
    Run the Quart app.

    :param host:        Host to run it on.
    :param port:        Port to run it on.
    :param debug:       Run server in debug mode?
    :param initdb:      Create models before running API?
    :param verbose:     Set logging to DEBUG instead of INFO
    """

    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    if not run_async(prepare_postgres(retries=6, interval=10.0)):
        exit(1)  # Connecting to our postgres server failed.

    if initdb:
        run_async(safe_create_tables(verbose=verbose))

    app.debug = debug

    config = Config()
    config.bind = [host + ":" + port]
    run_async(serve(app, config))


if __name__ == "__main__":
    ENV = load_env(
        fp="./local.env",
        args=("SECRET_KEY", "DB_URI", "DISCORD_CLIENT_ID", "DISCORD_CLIENT_SECRET"),
    )
    app.config.from_mapping(mapping=ENV)

    app.cli()
