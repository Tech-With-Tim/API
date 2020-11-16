from quart import current_app

from typing import List, Optional
from asyncpg.pool import Pool
from enum import Enum
import datetime

import utils
import db


class Token(db.Model):
    """
    Token class to store jwt and discord OAuth tokens.

    Database Attributes:
        Attributes stored in the `tokens` table.

        :param int user_id: The discord user this token relates to.
        :param str token: The token itself.
        :param str type: The token type (JWT / OAUTH2)
        :param :class:`datetime.datetime` expires_at: The time this token expires.
        :param dict data: Additional data related to the token.
    """

    __slots__ = ("user_id", "token", "type", "expires_at", "data")

    TYPES = Enum("TokenTypes", "JWT, OAUTH2")

    def __init__(
        self,
        user_id: int,
        token: str,
        type: str,
        expires_at: datetime.datetime,
        data: dict,
    ):
        self.user_id = user_id
        self.token = token
        self.type = type
        self.expires_at = expires_at
        self.data = data

    @classmethod
    async def create_table(cls, pool: Pool) -> str:
        """Create this table."""

        create_query = """
CREATE TABLE IF NOT EXISTS public.tokens
(
    user_id bigint NOT NULL,
    type character varying(5) NOT NULL,
    token text NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    data json NOT NULL
);
        """

        return await pool.execute(query=create_query)

    @classmethod
    async def drop_table(cls, pool: Pool):
        """Drop / Delete this table."""
        return await pool.execute("DROP TABLE IF EXISTS tokens CASCADE;")
