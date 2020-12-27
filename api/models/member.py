from postDB import Model, Column, types


import utils


class Member(Model):
    """
    User class based on some discord data extended to better suit our application.

    Database Attributes:
        Attributes stored in the `members` table.

        :param int id:              The members discord ID
        :param int guild_id:        The guild ID the member belongs to.
        :param bool verified:       Whether or not the Member has verified in the guild.
        :param float xp:            Members experience points.
    """

    id = Column(
        types.ForeignKey("users", "id", sql_type=types.String()),
        primary_key=True
    )

    guild_id = Column(
        types.ForeignKey("guilds", "id", sql_type=types.String()),
        primary_key=True
    )

    verified = Column(types.Boolean)
    xp = Column(types.Real)

    @property
    def created_at(self):
        return utils.snowflake_time(int(self.id))
