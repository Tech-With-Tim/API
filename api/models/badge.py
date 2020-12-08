from postDB import Model, Column, types


class Badge(Model):
    """
    Badge class created whenever a user should recieve a Badge.

    Database Attributes:
        Attributes stored in the `badges` table.

        :param int id:              The badge ID.  - Barely used.
        :param int user_id:         The user who recieved this badge.
        :param str asset:           The connected asset name
    """
    id = Column(types.Serial)
    user_id = Column(
        types.ForeignKey("users", "id", sql_type=types.Integer(big=True))
    )
    asset = Column(
        types.ForeignKey("assets", "name", sql_type=types.String(length=100))
    )