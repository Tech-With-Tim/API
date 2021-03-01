from http import HTTPStatus
from typing import Optional

import asyncpg
from postDB import Model, Column, types
from quart import exceptions


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
    async def insert(cls, member_id: int, role_id: int, *, user_id: Optional[int] = None):
        query = """SELECT * FROM add_role_to_member($1, $2, $3)"""

        try:
            await cls.pool.execute(query, role_id, member_id, user_id)
        except asyncpg.exceptions.DataError:
            http_status = HTTPStatus.FORBIDDEN
            http_status.description = "Missing Permissions"
            raise exceptions.Forbidden(http_status)
        except asyncpg.exceptions.UniqueViolationError:
            http_status = HTTPStatus.BAD_REQUEST
            http_status.description = "User already has that role"
            raise exceptions.BadRequest(http_status)

    @classmethod
    async def delete(cls, member_id: int, role_id: int, *, user_id: Optional[int] = None):
        query = """SELECT * FROM remove_role_from_member($1, $2, $3)"""

        try:
            await cls.pool.execute(query, role_id, member_id, user_id)
        except asyncpg.exceptions.DataError:
            http_status = HTTPStatus.FORBIDDEN
            http_status.description = "Missing Permissions"
            raise exceptions.Forbidden(http_status)
