from api import app

from typing import Any, Coroutine
from quart import Quart
import logging
import asyncpg
import asyncio
import click
import json
import sys
import os


env = {"SECRET_KEY": None, "DB_URI": None}


loop = asyncio.get_event_loop()


for key in env.keys():
    try:
        env[key] = os.environ[key]
    except KeyError:
        sys.stderr.write(f"Found no `{key}` var in env, exiting..."), exit(1)

app.config.from_mapping(mapping=env)

# TODO: Handle environment values in docker.
#       https://docs.docker.com/compose/environment-variables/


def run_async(func: Coroutine) -> Any:
    """Run a coroutine in a function."""
    return loop.run_until_complete(func)


async def setup_db(quart_app: Quart) -> asyncpg.pool.Pool:
    log = logging.getLogger("DB")

    async def init(con: asyncpg.connection.Connection) -> None:
        await con.set_type_codec(
            "json", schema="pg_catalog", encoder=json.dumps, decoder=json.loads
        )

    log.debug("Attempting to initialize database connection.")

    pool = await asyncpg.create_pool(
        dsn=env["DB_URI"], min_size=1, init=init, loop=loop
    )

    log.debug("Connected to database `{}`".format(env["DB_URI"].split("/")[-1]))

    quart_app.db = pool

    return pool


run_async(setup_db(quart_app=app))


@app.cli.command()
def initdb():
    async def init_db():
        from db import models

        for model in models.__all__:
            print(await model.create_table(pool=app.db))
            click.echo(f"Creating table {model.__name__}")

    run_async(init_db())


@app.cli.command()
def dropdb():
    async def drop_db():
        from db import models

        for model in models.__all__:
            print(await model.drop_table(pool=app.db))
            click.echo(f"Dropping table {model.__name__}")

    run_async(drop_db())


@app.cli.command()
def runserver():
    app.run(loop=loop, debug=False, use_reloader=False)


if __name__ == "__main__":
    app.cli()
