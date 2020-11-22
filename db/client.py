from typing import Optional, List, Union, Any
from logging import getLogger
import textwrap
import asyncio
import asyncpg
import json

from db import models


log = getLogger("DB")


class Client:
    """
    Client class so we dont have to keep on writing queries over and over.
    """

    def __init__(
        self, pool: asyncpg.pool.Pool, *, timeout: float = 10.0, max_cons: int = 10
    ):
        self.pool = pool
        self.timeout = timeout
        self.max_cons = max_cons

        self.semaphore = asyncio.Semaphore(value=max_cons)

    @classmethod
    async def create_pool(
        cls, uri: str, max_cons: int, timeout: float = 10.0, loop=None, **kwargs
    ) -> "Client":
        """
        Create a pool of
        :param str uri:         The dsn we want to connect to.
        :param int max_cons:    The max connections we can establish in our Pool.
        :param float timeout:   The max time we can allow queries to run.
        :param loop:           asyncio event loop
        :param dict kwargs:     Other kwargs we want to pass to the Pool instance.
        :return:
        """
        loop = loop or asyncio.get_event_loop()

        async def init(con: asyncpg.connection.Connection) -> None:
            await con.set_type_codec(
                "json", schema="pg_catalog", encoder=json.dumps, decoder=json.loads
            )

        pool = await asyncpg.create_pool(
            dsn=uri,
            init=init,
            loop=loop,
            min_size=1,
            max_size=max_cons,
            **kwargs,
        )

        return cls(pool=pool, timeout=timeout, max_cons=max_cons)

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Our own `fetch` coroutine to log when it is called."""
        async with self.semaphore:
            async with self.pool.acquire() as con:
                log.debug(
                    textwrap.dedent(
                        f"FETCH\nQUERY={textwrap.dedent(query)}"
                        f'\nARGS=[{", ".join(str(arg) for arg in args)}]'
                    )
                )
                return await con.fetch(query, *args, timeout=self.timeout)

    async def fetchrow(self, query: str, *args) -> Union[asyncpg.Record, None]:
        """Our own `fetchrow` coroutine to log when it is called."""
        async with self.semaphore:
            async with self.pool.acquire() as con:
                log.debug(
                    textwrap.dedent(
                        f"FETCHROW\nQUERY={textwrap.dedent(query)}"
                        f'\nARGS=[{", ".join(str(arg) for arg in args)}]'
                    )
                )
                return await con.fetchrow(query, *args, timeout=self.timeout)

    async def fetchval(self, query: str, *args) -> Union[Any, None]:
        """Our own `fetchval` coroutine to log when it is called."""
        async with self.semaphore:
            async with self.pool.acquire() as con:
                log.debug(
                    textwrap.dedent(
                        f"FETCHVAL\nQUERY={textwrap.dedent(query)}"
                        f'\nARGS=[{", ".join(str(arg) for arg in args)}]'
                    )
                )
                return await con.fetchval(query, *args, timeout=self.timeout)

    async def execute(self, query: str, *args) -> Union[Any, None]:
        """Our own `execute` coroutine to log when it is called."""
        async with self.semaphore:
            async with self.pool.acquire() as con:
                log.debug(
                    textwrap.dedent(
                        f"EXECUTE\nQUERY={textwrap.dedent(query)}"
                        f'\nARGS=[{", ".join(str(arg) for arg in args)}]'
                    )
                )
                return await con.execute(query, *args, timeout=self.timeout)

    async def get_user(self, id: int) -> Optional[models.User]:
        """
        Tries to fetch a `User` instance from the database.

        :param int id:      The users Discord ID.
        :returns            Optional[models.User]
        """

        record = await self.fetchrow("SELECT * FROM users WHERE id = $1;", id)
        if record is None:
            return None

        return models.User(**record)

    async def get_token(self, user_id: int, type: str) -> Optional[models.Token]:
        """
        Get the token object matching provided arguments.

        :param user_id:     Discord ID of the token user.
        :param type:        Which type of token you are requesting.
        :return:            Optional[models.Token]
        """
        query = """
        SELECT * FROM tokens
        WHERE user_id = $1
        AND type = $2;
        """

        record = await self.fetchrow(query, user_id, type)
        if record is None:
            return None

        return models.Token(**record)
