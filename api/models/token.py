from postDB import Model, Column, types
from enum import Enum


TYPES = Enum("TokenTypes", "JWT OAuth2")


class Token(Model):
    """
    Token class to store JWT and OAuth2 tokens.

    Database Attributes:
        Attributes stored in the `tokens` table.

        :param int user_id: The discord user this token relates to.
        :param str token: The token itself.
        :param str type: The token type (JWT / OAUTH2)
        :param :class:`datetime.datetime` expires_at: The time this token expires.
        :param dict extra: Additional data related to the token.

    """

    user_id = Column(
        types.ForeignKey("users", "id", sql_type=types.Integer(big=True)),
        primary_key=True,
    )
    type = Column(
        types.String(length=10),
        primary_key=True
    )
    token = Column(types.String)
    expires_at = Column(types.DateTime)
    extra = Column(types.JSON)

    async def update(self):
        """Update the database with currently saved data."""
        query = """
            INSERT INTO tokens ( user_id, type, token, expires_at, extra )
                VALUES ( $1, $2, $3, $4, $5 )
                ON CONFLICT (user_id, type) DO UPDATE SET
                    expires_at = $4,
                    token = $3,
                    data = $5
        """

        con = await self.ensure_con()

        return await con.execute(
            query, self.user_id, self.type, self.type, self.expires_at, self.extra
        )

    async def delete(self) -> str:
        """Delete the token from the database."""
        query = """
            DELETE FROM tokens 
            WHERE 
                user_id = $1 
            AND 
                type = $2
        """

        con = await self.ensure_con()

        return await con.execute(query, self.user_id, self.type)
