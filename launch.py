import logging
import asyncio
import asyncpg
import config
import click

from uvicorn import Config, Server
from typing import Any, Coroutine
from postDB import Model

logging.basicConfig(level=logging.INFO)


try:
    import uvloop  # noqa f401
except ModuleNotFoundError:
    loop = asyncio.new_event_loop()
else:
    loop = uvloop.new_event_loop()

asyncio.set_event_loop(loop)


def run_async(coro: Coroutine) -> Any:
    """
    Used to run coroutines outside any coroutine.

    :param coro:    The coroutine to run.
    :returns:       Whatever the coroutine returned.
    """
    return asyncio.get_event_loop().run_until_complete(coro)


async def prepare_postgres(
    retries: int = 5,
    interval: float = 10.0,
    db_uri: str = None,
    loop: asyncio.AbstractEventLoop = None,
) -> bool:
    """
    Prepare the postgres database connection.

    :param int retries:             Included to fix issue with docker starting API before DB is finished starting.
    :param float interval:          Interval of which to wait for next retry.
    :param str db_uri:              DB URI to connect to.
    :param AbstractEventLoop loop:  Asyncio loop to run the pool with.
    """

    log = logging.getLogger("DB")
    db_name = db_uri.split("/")[-1]
    log.info('[i] Attempting to connect to DB "%s"' % db_name)
    for i in range(1, retries + 1):
        try:
            await Model.create_pool(
                uri=db_uri,
                max_con=10,  # We might want to increase this number in the future.
                loop=loop,
            )

        except asyncpg.InvalidPasswordError as e:
            log.error("[!] %s" % str(e))
            return False

        except (ConnectionRefusedError,):
            log.warning(
                "[!] Failed attempt #%s/%s, trying again in %ss"
                % (i, retries, interval)
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

    with open("snowflake.sql") as f:
        query = f.read()

        if verbose:
            print(query)

        await Model.pool.execute(query)

    for model in models_ordered:
        await model.create_table(verbose=verbose)
        log.info("Created table %s" % model.__tablename__)


async def delete_tables(verbose: bool = False):
    """
    Delete all tables.

    :param verbose:     Whether or not to print the postgres statements being executed.
    """

    log = logging.getLogger("DB")

    for model in Model.all_models():
        await model.drop_table(verbose=verbose)
        log.info("Dropped table %s" % type(model).__tablename__)

    await Model.pool.execute("DROP FUNCTION IF EXISTS create_snowflake")
    await Model.pool.execute("DROP SEQUENCE IF EXISTS global_snowflake_id_seq")


@click.group()
def cli():
    pass


@cli.command(name="initdb")
@click.option("-v", "--verbose", default=False, is_flag=True)
def _initdb(verbose: bool):
    """
    Creates all tables defined in the app.

    :param verbose:     Print SQL statements when creating models?
    """
    if not run_async(
        prepare_postgres(
            retries=6, interval=10.0, db_uri=config.postgres_uri(), loop=loop
        )
    ):
        exit(1)  # Connecting to our postgres server failed.

    run_async(safe_create_tables(verbose=verbose))


@cli.command(name="dropdb")
@click.option("-v", "--verbose", default=False, is_flag=True)
def _dropdb(verbose: bool):
    """
    Drops all tables defined in the app.

    :param verbose:     Print SQL statements when dropping models?
    """
    if not run_async(
        prepare_postgres(
            retries=6, interval=10.0, db_uri=config.postgres_uri(), loop=loop
        )
    ):
        exit(1)  # Connecting to our postgres server failed.

    run_async(delete_tables(verbose=verbose))


@cli.command()
@click.option("-p", "--port", default=5000)
@click.option("-h", "--host", default="127.0.0.1")
@click.option("-d", "--debug", default=False, is_flag=True)
@click.option("-i", "--initdb", default=False, is_flag=True)
@click.option("-r", "--resetdb", default=False, is_flag=True)
@click.option("-v", "--verbose", default=False, is_flag=True)
def runserver(
    host: str, port: str, debug: bool, initdb: bool, resetdb: bool, verbose: bool
):
    """
    Run the FastAPI Server.

    :param host:        Host to run it on.
    :param port:        Port to run it on.
    :param debug:       Run server in debug mode?
    :param initdb:      Create models before running API?
    :param verbose:     Set logging to DEBUG instead of INFO
    """
    config.set_debug(debug)

    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    if not run_async(
        prepare_postgres(
            retries=6, interval=10.0, db_uri=config.postgres_uri(), loop=loop
        )
    ):
        exit(1)  # Connecting to our postgres server failed.

    server_config = Config("api.app:app", host=host, port=port, debug=debug)
    server = Server(config=server_config)

    async def worker():
        if initdb:
            await safe_create_tables(verbose=verbose)
        elif resetdb:
            await delete_tables(verbose=verbose)
            await safe_create_tables(verbose=verbose)

        await server.serve()

    run_async(worker())


if __name__ == "__main__":
    cli()
