from postDB import Model, Column, types
from typing import Optional, Union
from datetime import datetime

import utils


VALID_STATIC_FORMATS = frozenset({"jpeg", "jpg", "webp", "png"})
VALID_AVATAR_FORMATS = VALID_STATIC_FORMATS | {"gif"}


class User(Model):
    """
    User class based on some discord data extended to better suit our application.

    Database Attributes:
        Attributes stored in the `users` table.

        :param int id:              The users Discord ID
        :param str username:        The users discord username.
        :param int discriminator:   The users discord discriminator.
        :param str avatar:          The users avatar hash, could be None.
        :param str type:            The type of User this is.  USER|APP
    """

    id = Column(types.Integer(big=True), primary_key=True)
    # Store the ID as a BIGINT even though it's transferred as a string.
    # This is due to a substantial difference in index time and storage space
    username = Column(types.String(length=32), unique=True)
    discriminator = Column(types.String(length=4), unique=True)
    avatar = Column(types.String, nullable=True)
    type = Column(types.String, default="USER")

    @classmethod
    async def fetch(cls, id: Union[str, int]) -> Optional["User"]:
        """Fetch a user with the given ID."""
        query = "SELECT * FROM users WHERE id = $1"
        user = await cls.pool.fetchrow(query, int(id))

        if user is not None:
            user = cls(**user)

        return user

    @classmethod
    async def create(
        cls,
        id: Union[str, int],
        username: str,
        discriminator: str,
        avatar: str = None,
        type: str = "USER",
    ) -> Optional["User"]:
        """
        Create a new User instance.

        Returns the new instance if created.
        Returns `None` if a Unique Violation occurred.
        """
        query = """
        INSERT INTO users (id, username, discriminator, avatar, type)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT DO NOTHING
        RETURNING *;
        """

        record = await cls.pool.fetchrow(
            query, int(id), username, discriminator, avatar, type
        )

        if record is None:
            return None

        return cls(**record)

    @property
    def created_at(self) -> datetime:
        """Returns """
        return utils.snowflake_time(self.id)

    def is_avatar_animated(self) -> bool:
        """Indicates if the user has an animated avatar."""
        return bool(self.avatar and self.avatar.startswith("a_"))

    @property
    def default_avatar_url(self) -> str:
        return "https://cdn.discordapp.com/embed/avatars/%s.png" % (
            int(self.discriminator) % 5
        )

    @property
    def avatar_url_as(self, *, fmt=None, static_format="webp", size=1024):
        if not size & (size - 1) and size in range(16, 4097):
            raise RuntimeWarning("size must be a power of 2 between 16 and 4096")
        if fmt is not None and fmt not in VALID_AVATAR_FORMATS:
            raise RuntimeWarning(
                "format must be None or one of {}".format(VALID_AVATAR_FORMATS)
            )

        if fmt == "gif" and not self.is_avatar_animated():
            raise RuntimeWarning("non animated avatars do not support gif format")
        if static_format not in VALID_STATIC_FORMATS:
            raise RuntimeWarning(
                "static_format must be one of {}".format(VALID_STATIC_FORMATS)
            )

        if self.avatar is None:
            return self.default_avatar_url + "?size=%s" % size

        if fmt is None:
            fmt = "gif" if self.is_avatar_animated() else static_format

        return (
            "https://cdn.discordapp.com/avatars"
            "/{0.id}/{0.avatar}.{1}?size={2}".format(self, fmt, size)
        )
