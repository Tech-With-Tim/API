from postDB import Model, Column, types

from typing import Optional, List, Union
from datetime import datetime  # noqa f401
import logging
import asyncpg

from .permission import Permission
import utils

log = logging.getLogger("Roles")


class Role(Model):
    """
    Role class used in ACL
    Database Attributes:
        Attributes stored in the `roles` table.
        :param int id:                          Role (Snowflake) ID.
        :param str name:                        Role name.
        :param int position:                    The position this role is in the hierarchy.
        :param int color:                       The color this role is.
        :param int permissions:                 The permissions this role has.
        :param :class:`datetime` created_at:    The time this role was created at.
    """

    id = Column(types.Integer(big=True), unique=True)
    name = Column(types.String(length=32))
    position = Column(types.Integer(), unique=True)
    color = Column(types.Integer())
    permissions = Column(types.Integer())

    def __repr__(self):
        return (
            '<Role id="{0.id}" name="{0.name}" '
            'permissions="{0.permissions}" position="{0.position}">'.format(self)
        )

    @classmethod
    async def create(
        cls,
        name: str,
        position: int,
        color: int,
        permissions: int,
    ):
        """Create a new Role, if one does not already exist."""
        query = """
        INSERT INTO roles (id, name, position, color, permissions)
            VALUES (create_snowflake(), $1, $2, $3, $4)
            RETURNING *;
        """

        record = await cls.pool.fetchrow(query, name, position, color, permissions)

        return cls(**record)

    @classmethod
    async def fetch(cls, id: Union[str, int]) -> Optional["Role"]:
        """Fetch a role with the given ID."""
        query = "SELECT * FROM roles WHERE id = $1"
        role = await cls.pool.fetchrow(query, int(id))

        if role is not None:
            role = cls(**role)

        return role

    @property
    def created_at(self):
        return utils.internal_snowflake_time(self.id)

    def has_permission(self, permission: "Permission") -> bool:
        """Returns `True` if this Role has said `Permission`"""
        if not isinstance(permission, Permission):
            return False

        if self.permissions & (1 << Permission.ADMINISTRATOR) == (
            1 << Permission.ADMINISTRATOR
        ):
            return True  # Admins have all perms

        return (self.permissions & (1 << permission.value)) == (1 << permission.value)

    @classmethod
    async def create_all(cls, verbose: bool = False) -> List["Role"]:
        """Create all base roles required for the website."""

        roles = [
            {
                "name": "Admin",
                "position": 1,
                "color": 0x31D5CF,
                "permissions": 1 << Permission.ADMINISTRATOR,
            },
            {
                "name": "Developer",
                "position": 2,
                "color": 0xFFDF00,
                "permissions": 1 << Permission.ADMINISTRATOR,
            },
            {
                "name": "Timathon Host",
                "position": 3,
                "color": 0,
                "permissions": 1 << Permission.MANAGE_TIMATHON
                | 1 << Permission.BAN_TIMATHON
                | 1 << Permission.KICK_TIMATHON_PARTICIPANTS
                | 1 << Permission.CREATE_TIMATHON
                | 1 << Permission.VIEW_TIMATHON_SUBMISSIONS,
            },
        ]

        ret = []

        for role in roles:
            try:
                if verbose:
                    log.info("Creating role: " + str(role))
                role = await cls.create(**role)
                ret.append(role)
            except asyncpg.UniqueViolationError:
                log.error(
                    "Failed to create new role, UniqueViolationError on role: "
                    + role["name"]
                )
                continue

        return ret
