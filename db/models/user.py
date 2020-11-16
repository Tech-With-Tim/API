from quart import current_app

from typing import List, Optional
from asyncpg.pool import Pool
from enum import Enum

from db import Model
import utils


Badge = object
Ban = object
# TODO: Implement real Badge & Ban classes ^


class User(Model):
    """
    User class based of some discord user data then extended with more data relevant to our application.

    Database Attributes:
        Attributes stored in the `users` table.

        :param int id: The users Discord ID.
        :param str username: The users discord username.
        :param str discriminator: The users discord discriminator.
        :param str avatar: The users avatar hash, could be None.

        :param int xp: The users Experience points.
        :param float coins: The amount of coins the user has.
        :param bool verified: Has the user completed captcha verification in discord?

    Discord Attributes:
        These should all be fetched through the BOT api and cached

    Additional Database properties:
        These properties are stored in the database, but not in the same table as user data.

        :prop List[Badge] badges: A list of Badges this user has received.
        :prop List[Ban] bans: A list of bans the user currently has.
    """

    __slots__ = (
        "id",
        "username",
        "discriminator",
        "avatar",
        "xp",
        "type",
        "coins",
        "verified",
    )

    TYPES = Enum("UserTypes", "USER BOT APP")

    def __init__(
        self,
        id: int,
        username: str,
        discriminator: str,
        avatar: Optional[str],
        xp: int = 0,
        type: str = "user",
        coins: float = 0.0,
        verified: bool = False,
    ):
        self.id = id
        self.username = username
        self.discriminator = discriminator
        self.avatar = avatar

        self.xp = xp
        self.type = type
        self.coins = coins
        self.verified = verified

    @classmethod
    async def create_table(cls, pool: Pool):
        """Create this table."""
        create_query = """
CREATE TABLE IF NOT EXISTS public.users
(
    id bigint NOT NULL,
    username character varying(32),
    discriminator character varying(4) NOT NULL,
    avatar character varying(100),
    xp real NOT NULL,
    type character varying(10) NOT NULL,
    coins real NOT NULL,
    verified boolean NOT NULL,
    PRIMARY KEY (id)
);
        """

        return await pool.execute(query=create_query)

    @classmethod
    async def drop_table(cls, pool: Pool):
        """Drop / Delete this table."""
        return await pool.execute("DROP TABLE IF EXISTS users CASCADE;")

    @property
    def created_at(self):
        return utils.snowflake_time(self.id)

    async def create(self) -> bool:
        """
        Post a new User instance.

        Returns a bool informing you if a new User was inserted or not.
        """
        query = """
        INSERT INTO users (id, username, discriminator, avatar, xp, type, coins, verified)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (id) DO NOTHING;
        """

        response = await current_app.db.execute(
            query,
            self.id,
            self.username,
            self.discriminator,
            self.avatar,
            self.xp,
            self.type,
            self.coins,
            self.verified,
        )

        return response.split()[-1] == "1"

    @property
    async def badges(self) -> List[Badge]:
        return []

    @property
    async def bans(self) -> List[Ban]:
        return []
