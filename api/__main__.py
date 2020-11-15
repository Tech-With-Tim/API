from api import app

from typing import Any, Coroutine
from quart import Quart
import asyncpg
import asyncio
import click
import json
import sys
import os


env = {
    "SECRET_KEY": None,
    "DB_URI": None
}

for key in env.keys():
    try:
        env[key] = os.environ[key]
    except KeyError:
        sys.stderr.write(
            f"Found no `{key}` var in env, exiting..."
        ), exit(1)

app.config.from_mapping(mapping=env)

# TODO: Handle environment values in docker.
#       https://docs.docker.com/compose/environment-variables/


def run_async(func: Coroutine) -> Any:
    """Run a coroutine in a function."""
    return asyncio.get_event_loop(
    ).run_until_complete(
        func
    )


async def setup_db(quart_app: Quart) -> asyncpg.pool.Pool:
    async def init(con: asyncpg.connection.Connection) -> None:
        await con.set_type_codec(
            "json", schema="pg_catalog", encoder=json.dumps, decoder=json.loads
        )

    pool = await asyncpg.create_pool(
        dsn=env["DB_URI"],
        init=init
    )

    app.db = pool

    return pool


run_async(
    setup_db(quart_app=app)
)


@app.cli.command()
def initdb():
    async def init_db():
        from db import models

        for model in models.__all__:
            await model.create_table()
            click.echo(f"Creating table {model.__name__}")

    run_async(init_db())


@app.cli.command()
def runserver():
    app.run(
        debug=True,
        use_reloader=False
    )


if __name__ == '__main__':
    app.cli()
