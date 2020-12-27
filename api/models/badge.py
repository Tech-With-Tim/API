from postDB import Model, Column, types


class Badge(Model):
    """
    Badge class created whenever a user should recieve a Badge.

    Database Attributes:
        Attributes stored in the `badges` table.

        :param int id:              The badge ID.  - Barely used.
        :param str user_id:         The user who recieved this badge.
        :param str asset:           The connected asset name
    """
    id = Column(types.Serial)
    name = Column(types.String)
    user_id = Column(
        types.ForeignKey("users", "id", sql_type=types.String())
    )
    asset = Column(
        types.ForeignKey("assets", "name", sql_type=types.String(length=100))
    )
