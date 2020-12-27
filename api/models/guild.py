from postDB import Model, Column, types
from typing import Optional

import utils


class Guild(Model):
    """

    Database Attributes:
        Attributes stored in the `guilds` table.

        :param int id:                          The Guild ID.
        :param str name:                        The Guild name.
        :param str region:                      The Guild region [EU/NAW/NAE/...]
        :param str icon_hash:                   The guilds icon hash.
        :param int owner_id:                    The owner of the guild.
        :param int muted_role_id:               Muted role ID.
        :param int log_channel_id:              Log channel ID.
        :param int verification_channel_id:     Verification channel
    """

    id = Column(types.String(), primary_key=True)
    name = Column(types.String(length=100))
    region = Column(types.String)
    icon_hash = Column(types.String)
    owner_id = Column(types.Integer(big=True))
    muted_role_id = Column(types.Integer(big=True), nullable=True)
    log_channel_id = Column(types.Integer(big=True), nullable=True)
    verification_channel_id = Column(types.Integer(big=True), nullable=True)

    @property
    def created_at(self):
        return utils.snowflake_time(int(self.id))

    @classmethod
    async def fetch(cls, id: int) -> Optional["Guild"]:
        query = "SELECT * FROM {} WHERE id = $1".format(cls.__tablename__)

        record = await cls.pool.fetchrow(query, id)
        if record is None:
            return None

        return cls(**record)

    async def create(self) -> bool:
        """
        Post a new Guild instance.

        Returns a bool informing you if a new User object was inserted or not.
        """
        query = """
        INSERT INTO users (id, name, icon_hash, muted_role_id, log_channel_id)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT DO NOTHING;
        """

        response = await self.pool.execute(
            query,
            self.id,
            self.name,
            self.icon_hash,
            self.muted_role_id,
            self.log_channel_id
        )

        return response.split()[-1] == "1"

    async def update(self, **new_kwargs):
        verified = {}

        for arg in [col.name for col in self.columns if col.name != "id"]:
            try:
                value = new_kwargs[arg]
            except KeyError:
                continue

            column: Column = getattr(self, arg)

            check = column.column_type.python
            if value is None and not column.nullable:
                raise TypeError('Cannot pass None to non-nullable column %s.' % column.name)
            elif not check or not isinstance(value, check):
                fmt = 'column {0.name} expected {1.__name__}, received {2.__class__.__name__}'
                raise TypeError(fmt.format(column, check, value))

            verified[arg] = value
            setattr(self, arg, value)

        query = """UPDATE guilds SET name = $1, muted_role_id = $2, log_channel_id = $3"""
        return await self.pool.execute(query, self.name, self.muted_role_id, self.log_channel_id)
