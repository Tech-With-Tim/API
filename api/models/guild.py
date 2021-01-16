from postDB import Model, Column, types
from typing import Any, Dict, Optional, Union
from datetime import datetime

import utils


VALID_STATIC_FORMATS = frozenset({"jpeg", "jpg", "webp", "png"})
VALID_ICON_FORMATS = VALID_STATIC_FORMATS | {"gif"}


class Guild(Model):
    """
    Guild model for storing information about discord guilds.

    :param int id:          The guilds id.
    :param str name:        The guilds name.
    :param int owner_id:    The guilds owner id.
    :param str icon_hash:   The guilds icon hash.

    """

    id = Column(types.Integer(big=True), primary_key=True)
    name = Column(types.String())
    owner_id = Column(types.Integer(big=True))
    icon_hash = Column(types.String(), nullable=True)

    @classmethod
    async def fetch(cls, id: Union[str, int]) -> Optional["Guild"]:
        """Fetch a guild with the given ID."""
        query = "SELECT * FROM guilds WHERE id = $1"
        record = await cls.pool.fetchrow(query, int(id))

        if record is None:
            return None

        return cls(**record)

    @classmethod
    async def create(
        cls,
        id: Union[str, int],
        name: str,
        owner_id: Union[str, int],
        icon_hash: Optional[str] = None,
    ) -> Optional["Guild"]:
        """
        Create a new Guild instance.

        Returns the new instance if created.
        Returns `None` if a Unique Violation occurred.
        """

        query = """
        INSERT INTO guilds (id, name, owner_id, icon_hash)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT DO NOTHING
        RETURNING *;
        """

        record = await cls.pool.fetchrow(query, int(id), name, int(owner_id), icon_hash)

        if record is None:
            return None

        return cls(**record)

    async def update(self, **fields) -> Optional["Guild"]:
        """Update the Guild with the given arguments."""

        if not fields:
            return self

        allowed_fields = ("name", "owner_id", "icon_hash")
        fields = {name: fields.get(name, getattr(self, name)) for name in allowed_fields}

        if "owner_id" in fields:
            fields["owner_id"] = int(fields["owner_id"])

        query = """
        UPDATE guilds
        SET (name, owner_id, icon_hash) = ($2, $3, $4)
        WHERE id = $1
        RETURNING *;
        """
        record = await self.pool.fetchrow(
            query, int(self.id), fields["name"], fields["owner_id"], fields["icon_hash"]
        )

        if record is None:
            return None

        for field, value in record.items():
            setattr(self, field, value)

        return self

    async def delete(self) -> Optional["Guild"]:
        """Delete the Guild."""

        query = """
        DELETE FROM guilds
        WHERE id = $1
        RETURNING *;
        """
        record = await self.pool.fetchrow(query, int(self.id))

        if record is None:
            return None

        for field, value in record.items():
            setattr(self, field, value)

        return self

    @property
    def created_at(self) -> datetime:
        """Returns datetime of the guild creation."""
        return utils.snowflake_time(self.id)

    def is_icon_animated(self) -> bool:
        """Indicates if the guild has an animated icon."""
        return bool(self.icon_hash and self.icon_hash.startswith("a_"))

    def icon_url_as(self, *, format=None, static_format="webp", size=1024) -> Optional[str]:
        if not size & (size - 1) and size in range(16, 4097):
            raise RuntimeWarning("size must be a power of 2 between 16 and 4096")
        if format is not None and format not in VALID_ICON_FORMATS:
            raise RuntimeWarning("format must be None or one of {}".format(VALID_ICON_FORMATS))
        if format == "gif" and not self.is_icon_animated():
            raise RuntimeWarning("non animated avatars do not support gif format")
        if static_format not in VALID_STATIC_FORMATS:
            raise RuntimeWarning("static_format must be one of {}".format(VALID_STATIC_FORMATS))

        if self.icon_hash is None:
            return None

        if format is None:
            format = "gif" if self.is_icon_animated() else static_format

        return "https://cdn.discordapp.com/icons/{0.id}/{0.icon_hash}.{1}?size={2}".format(
            self, format, size
        )
