from postDB import Model, Column, types
from quart import exceptions
from typing import Optional, List, Union
from datetime import datetime  # noqa f401
from http import HTTPStatus
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
        :param bool base                        Determines if the role is a base role or not
        :param :class:`datetime` created_at:    The time this role was created at.
    """

    id = Column(types.Integer(big=True), unique=True)
    name = Column(types.String(length=32))
    position = Column(types.Integer(), unique=True)
    color = Column(types.Integer())
    permissions = Column(types.Integer())
    base = Column(types.Boolean(), default=False)

    def __repr__(self):
        return (
            '<Role id="{0.id}" name="{0.name}" '
            'permissions="{0.permissions}" position="{0.position}">'.format(self)
        )

    @classmethod
    async def create(
            cls,
            name: str,
            color: int,
            permissions: int,
            base: Optional[bool] = False
    ):
        """Create a new Role, if one does not already exist."""
        query = """
        INSERT INTO roles (id, name, position, color, permissions, base)
            VALUES (
                create_snowflake(), 
                $1,
                ((SELECT COUNT(*) FROM roles) + 1),
                $2,
                $3,
                $4
            )
            RETURNING *;
        """

        record = await cls.pool.fetchrow(query, name, color, permissions, base)

        return cls(**record)

    async def update(self, *, user_id: int = None, **data):
        """Update Role Data"""
        update_query = ["UPDATE roles SET"]

        fields = ("name", "color", "permissions",)
        new_data = {
            field: data[field]
            for field in fields if field in data.keys()
        }

        if len(new_data) > 0:
            update_query.append(", ".join("%s = $%d" % (key, i) for i, key in enumerate(new_data.keys(), 2)))

            update_query.append("WHERE roles.id = $1 RETURNING *, id::TEXT")

            query = " ".join(update_query)
            record = await self.pool.fetchrow(
                query,
                int(self.id),
                *new_data.values(),
            )

            if record is None:
                return None

            for field, value in record.items():
                setattr(self, field, value)

        if self.position != data.get("position", self.position):
            query = """SELECT COUNT(*) FROM roles;"""
            result = await self.pool.fetchrow(query)
            count = int(result["count"])

            position_query = """SELECT * FROM move_roles($1, $2::BIGINT, $3, $4);"""

            try:
                await self.pool.execute(
                    position_query,
                    max(0, min(int(data["position"]), count)),
                    int(self.id),
                    user_id,
                    self.position,
                )
            except asyncpg.exceptions.DataError:
                http_status = HTTPStatus.FORBIDDEN
                http_status.description = "You don't have permission to move that role"
                raise exceptions.Forbidden(http_status)

            self.position = data["position"]

        return self

    @classmethod
    async def fetch(cls, id: Union[str, int]) -> Optional["Role"]:
        """Fetch a role with the given ID."""
        query = """
        SELECT 
            id::TEXT,
            name,
            position,
            color,
            permissions
        FROM roles WHERE id = $1
        """
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
                "name": "Challenge Host",
                "position": 3,
                "color": 0,
                "permissions": 1 << Permission.MANAGE_CHALLENGE
                | 1 << Permission.BAN_CHALLENGE
                | 1 << Permission.KICK_CHALLENGE_PARTICIPANTS
                | 1 << Permission.CREATE_CHALLENGE
                | 1 << Permission.VIEW_CHALLENGE_SUBMISSIONS,
            },
        ]

        ret = []

        for data in roles:
            try:
                if verbose:
                    log.info("Creating role: " + str(data))

                query = """
                    SELECT * FROM roles WHERE base = TRUE and name = $1;
                """

                record = await cls.pool.fetchrow(query, data["name"])
                if record:
                    role = cls(**record)
                    log.info("Role %s already exists" % role.name)
                else:
                    position = int(data.pop("position"))
                    role = await cls.create(base=True, **data)
                    await role.update(position=position)
                ret.append(role)
            except asyncpg.UniqueViolationError:
                log.error(
                    "Failed to create new role, UniqueViolationError on role: "
                    + data["name"]
                )
                continue

        return ret

    @classmethod
    async def fetch_or_404(cls, id: Union[str, int]) -> Optional["Role"]:
        """
        Fetch a role with the given ID or send a 404 error.

        :param Union[str, int] id: The role's id.
        """

        if role := await cls.fetch(id):
            return role

        http_status = HTTPStatus.NOT_FOUND
        http_status.description = f"Role with ID {id} doesn't exist."
        raise exceptions.NotFound(http_status)

    @classmethod
    async def delete(cls, id: Union[str, int], *, user_id: Optional[int] = None):
        try:
            query = """SELECT * FROM delete_role($1, $2)"""
            print(user_id)
            await cls.pool.execute(query, id, user_id)
        except asyncpg.exceptions.DataError:
            http_status = HTTPStatus.FORBIDDEN
            http_status.description = "You don't have permission to delete that role"
            raise exceptions.Forbidden(http_status)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "position": self.position,
            "permissions": self.permissions,
        }
