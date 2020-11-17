from quart import current_app

from typing import Any
from asyncpg.pool import Pool
from enum import Enum
import datetime

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

    # Initialized attribute.
    # We have this attribute so attributes `user_id, type` cannot be changed after initialization.
    __initialized = False

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

        self.__initialized = True

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
            data json NOT NULL,
            PRIMARY KEY (user_id, type)
        );
        """

        return await pool.execute(query=create_query)

    @classmethod
    async def drop_table(cls, pool: Pool):
        """Drop / Delete this table."""
        return await pool.execute("DROP TABLE IF EXISTS tokens CASCADE;")

    async def update(self):
        """Update the database with currently saved data."""
        query = """
            INSERT INTO tokens ( user_id, type, token, expires_at, data )
                VALUES ( $1, $2, $3, $4, $5 )
                ON CONFLICT (user_id, type) DO UPDATE SET
                    data = $5,
                    token = $3,
                    expires_at = $4                    
        """

        return await current_app.db.execute(
            query, self.user_id, self.type, self.type, self.expires_at, self.data
        )

    async def delete(self) -> str:
        """Delete the token from the database."""
        query = """
            DELETE FROM tokens 
            WHERE 
                user_id = $1 
            AND 
                type = $2
        """

        return await current_app.db.execute(query, self.user_id, self.type)

    def __setattr__(self, key: str, value: Any):
        """Change the __setattr__ function so we can only """
        if key not in ("token", "expires_at", "data"):
            if not self.__initialized:
                raise RuntimeWarning("Cannot set this attribute.")

        super().__setattr__(key, value)
