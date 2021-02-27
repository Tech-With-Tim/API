from postDB import Model, Column, types


class UserRole(Model):
    """
    User class based on some discord data extended to better suit our application.
    Database Attributes:
        Attributes stored in the `users` table.
        :param int user_id: The users Discord ID
        :param int role_id: The role ID (Snowflake)
    """

    user_id = Column(
        types.ForeignKey("users", "id", sql_type=types.Integer(big=True)),
        primary_key=True,
    )
    role_id = Column(
        types.ForeignKey("roles", "id", sql_type=types.Integer(big=True)),
        primary_key=True,
    )

    @classmethod
    async def insert(cls, user_id: int, role_id: int):
        query = """
        INSERT INTO userroles (user_id, role_id)
            VALUES ($1, $2)
            ON CONFLICT (user_id, role_id) DO NOTHING;
        """

        return await cls.pool.execute(query, user_id, role_id)

    @classmethod
    async def delete(cls, user_id: int, role_id: int):
        query = """
        DELETE FROM userroles WHERE user_id = $1 AND role_id = $2;
        """

        return await cls.pool.execute(query, user_id, role_id)
