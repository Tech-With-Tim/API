from postDB import Model, Column, types
from typing import Optional
from enum import Enum


import utils


class User(Model):
    """
    User class based on some discord data extended to better suit our application.

    Database Attributes:
        Attributes stored in the `users` table.

        :param int id:              The users Discord ID
        :param str username:        The users discord username.
        :param str discriminator:   The users discord discriminator.
        :param str avatar:          The users avatar hash, could be None.

        :param str type:            The type of User this is.  USER|APP
    """

    TYPES = Enum("UserTypes", "USER APP")
    default = "USER"

    id = Column(types.Integer(big=True), unique=True)
    username = Column(types.String(length=32), primary_key=True)
    discriminator = Column(types.String(length=32), primary_key=True)
    avatar = Column(types.String, nullable=True)

    type = Column(types.String, default="USER")

    @property
    def created_at(self):
        return utils.snowflake_time(self.id)

    async def create(self) -> bool:
        """
        Post a new User instance.

        Returns a bool informing you if a new User object was inserted or not.
        """
        query = """
        INSERT INTO users (id, username, discriminator, avatar, type)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT DO NOTHING;
        """

        con = await self.ensure_con()

        response = await con.execute(
            query,
            self.id,
            self.username,
            self.discriminator,
            self.avatar,
            self.type
        )

        return response.split()[-1] == "1"

    @classmethod
    async def fetch(cls, id: int) -> Optional["User"]:
        """Fetch a user with the given ID."""
        query = "SELECT * FROM {} WHERE id = $1".format(cls.__tablename__)
        user = await cls.pool.fetchrow(query, id)

        if user is not None:
            user = cls(**user)

        return user
