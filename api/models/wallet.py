from postDB import Model, Column, types


class Wallet(Model):
    """
    Database Attributes:
        :param int user_id:         The user ID
        :param int guild_id:        The guild ID
        :param float coins:         The members coins
        :param int tokens:          The members challenge tokens.
    """
    user_id = Column(
        types.ForeignKey("users", "id", sql_type=types.Integer(big=True)),
        primary_key=True
    )

    guild_id = Column(
        types.ForeignKey("guilds", "id", sql_type=types.Integer(big=True)),
        primary_key=True
    )

    coins = Column(types.Real)
    tokens = Column(types.Integer)
