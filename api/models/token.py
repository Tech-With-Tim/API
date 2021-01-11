from postDB import Model, Column, types


class Token(Model):
    """
    Token class to store OAuth2 Tokens.

    :param str token:                               The access_token sent from discord_data.
    :param dict data:                               All data returned by discord API.
    :param int user_id:                             The discord user this token relates to
    :param :class:`datetime.datetime` expires_at:   The time this access token expires.
                                                    You can still use the refresh_token to generate a new token.

    """

    user_id = Column(
        types.ForeignKey("users", "id", sql_type=types.Integer(big=True)),
        primary_key=True,
    )
    expires_at = Column(types.String())
    token = Column(types.String())
    data = Column(types.JSON())

    async def update(self):
        """Create or update the Token instance."""
        query = """
            INSERT INTO tokens ( user_id, expires_at, token, data )
                VALUES ( $1, $2, $3, $4 )
                ON CONFLICT (user_id) DO UPDATE SET
                    expires_at = $2,
                    token = $3,
                    data = $4
            """

        return await self.pool.execute(
            query, self.user_id, self.expires_at, self.token, self.data
        )
