from api import app

from typing import Any, Coroutine
from aiohttp import ClientSession
from postDB import Model
from quart import Quart
import logging
import asyncio
import click
import sys
import os


env = {
    "SECRET_KEY": None,
    "DB_URI": None,
    "DISCORD_CLIENT_ID": None,
    "DISCORD_CLIENT_SECRET": None,
}


loop = asyncio.get_event_loop()


try:
    with open(".env", "r") as f:
        env_file = {
            key: arg
            for (key, arg) in [line.strip().split("=") for line in f.readlines()]
        }
except FileNotFoundError:
    env_file = {}


for key in env.keys():
    try:
        env[key] = os.environ[key]
    except KeyError:
        try:
            env[key] = env_file[key]
        except KeyError:
            sys.stderr.write(f"Found no `{key}` var in env, exiting..."), exit(1)

app.config.from_mapping(mapping=env)


def run_async(func: Coroutine) -> Any:
    """Run a coroutine in a function."""
    return loop.run_until_complete(func)


async def setup_db() -> None:
    log = logging.getLogger("DB")

    log.debug("Attempting to initialize database connection.")

    await Model.create_pool(uri=env["DB_URI"], max_con=10, loop=loop)

    log.debug("Connected to database `{}`".format(env["DB_URI"].split("/")[-1]))


async def setup_session(quart_app: Quart) -> ClientSession:
    log = logging.getLogger("Session")

    log.debug("Initializing http ClientSession")

    quart_app.session = ClientSession(loop=loop)

    return quart_app.session


run_async(setup_db())
run_async(setup_session(quart_app=app))


@app.cli.command()
def initdb():
    async def init_db():
        from api.models import all_models

        for model in all_models:
            print(await model.create_table(verbose=True))
            click.echo(f"Creating table {model.__name__}")

    run_async(init_db())


@app.cli.command()
def dropdb():
    async def drop_db():
        from postDB import Model

        for model in Model.all_models():
            print(await model.drop_table(verbose=True))
            click.echo(f"Dropping table {model.__name__}")

    run_async(drop_db())


# TODO: Add CLI command to create APP user
# TODO: Add CLI command to add User to admin group.  (After we make groups)


@app.cli.command()
def runserver():
    app.run(loop=loop, debug=True, use_reloader=False)


if __name__ == "__main__":
    app.cli()
