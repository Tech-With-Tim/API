from postDB import Model, Column, types
from typing import Optional, Union


class GuildConfig(Model):
    guild_id = Column(
        types.ForeignKey("guilds", "id", sql_type=types.Integer(big=True)),
        primary_key=True,
    )
    xp_enabled = Column(types.Boolean())
    xp_multiplier = Column(types.Real())
    eco_enabled = Column(types.Boolean())
    muted_role_id = Column(types.Integer(big=True))
    do_logging = Column(types.Boolean())
    log_channel_id = Column(types.Integer(big=True))
    do_verification = Column(types.Boolean())
    verification_type = Column(types.String())  # enum
    verification_channel_id = Column(types.Integer(big=True))

    @classmethod
    async def fetch(cls, guild_id: Union[str, int]) -> Optional["GuildConfig"]:
        """Fetch a GuildConfig with the given guild ID."""
        query = "SELECT * FROM guildconfigs WHERE guild_id = $1"
        record = await cls.pool.fetchrow(query, int(guild_id))

        if record is None:
            return None

        return cls(**record)

    @classmethod
    async def create(
        cls,
        guild_id: Union[str, int],
        *,
        xp_enabled: Optional[bool] = False,
        xp_multiplier: Optional[float] = 1.0,
        eco_enabled: Optional[bool] = False,
        muted_role_id: Optional[Union[str, int]] = None,
        do_logging: Optional[bool] = False,
        log_channel_id: Optional[Union[str, int]] = None,
        do_verification: Optional[bool] = False,
        verification_type: Optional[str] = False,
        verification_channel_id: Optional[Union[str, int]] = None,
    ) -> Optional["GuildConfig"]:
        """
        Create a new GuildConfig instance.

        Returns the new instance if created.
        Returns `None` if a Unique Violation occurred.
        """

        query = """
        INSERT INTO guildconfigs (guild_id, xp_enabled, xp_multiplier, eco_enabled, muted_role_id,
        do_logging, log_channel_id, do_verification, verification_type, verification_channel_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT DO NOTHING
        RETURNING *;
        """

        record = await cls.pool.fetchrow(
            query,
            int(guild_id),
            xp_enabled,
            xp_multiplier,
            eco_enabled,
            int(muted_role_id),
            do_logging,
            int(log_channel_id),
            do_verification,
            verification_type,
            int(verification_channel_id),
        )

        if record is None:
            return None

        return cls(**record)

    async def update(self, **fields) -> Optional["GuildConfig"]:
        """Update the GuildConfig with the given arguments."""

        allowed_fields = (
            "xp_enabled",
            "xp_multiplier",
            "eco_enabled",
            "muted_role_id",
            "do_logging",
            "log_channel_id",
            "do_verification",
            "verification_type",
            "verification_channel_id",
        )
        fields = {
            name: value for name, value in fields.items() if name in allowed_fields
        }

        query = f"""
        UPDATE guildconfigs
        SET ({", ".join(fields)}) = ({", ".join("$" + str(i) for i in range(2, len(fields) + 2))})
        WHERE id = $1
        RETURNING *;
        """
        record = await self.pool.fetchrow(query, int(self.guild_id), *fields.items())

        if record is None:
            return None

        for field, value in record:
            setattr(self, field, value)

        return self
