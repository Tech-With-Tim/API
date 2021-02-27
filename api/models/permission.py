from postDB import Model, Column, types

from typing import List
import logging
import asyncpg

log = logging.getLogger("Permissions")


class Permission(Model):
    """
    Permission class
    Database Attributes:
        Attributes stored in the `permissions` table.
        :param int id:              Permission ID.
        :param str name:            Permission name.
        :param int value:           Permission value.
        :param bool public:         If this permission is publicly usable.
                                    If not, only global roles can use it.
        :param str help_text:       Text displayed next to the permission when managing roles.
    """

    id = Column(types.Serial(), unique=True)
    name = Column(types.String(length=32), primary_key=True)
    value = Column(types.Integer(), unique=True)

    public = Column(types.Boolean(), default=True)
    help_text = Column(types.String())

    def __repr__(self):
        return "<Permission name=\"{0.name}\" value=\"{0.value}\" help=\"{0.help_text}\">".format(self)

    @classmethod
    async def create(
            cls, name: str, value: int, help_text: str, public: bool = True
    ) -> "Permission":
        """Create a new permission, if one does not already exist."""
        query = """
        INSERT INTO permissions (name, value, public, help_text)
            VALUES ($1, $2, $3, $4)
            RETURNING *;
        """

        record = await cls.pool.fetchrow(query, name, value, public, help_text)

        return cls(**record)

    @classmethod
    async def create_all(cls, verbose: bool = False) -> List["Permission"]:
        """Create all permissions required for the website."""

        permissions = [
            {
                "name": "Administrator",
                "value": cls.ADMINISTRATOR,
                "public": False,
                "help_text": "Users with this permission will have every permission"
                             " and will also bypass all channel specific permissions or restrictions.",
            },
            {
                "name": "Manage Global Roles",
                "value": cls.MANAGE_ROLES,
                "public": False,
                "help_text": "Allows management and editing of global roles.",
            },
            {
                "name": "Create Timathon",
                "value": cls.CREATE_TIMATHON,
                "public": False,
                "help_text": "Users with this permission will be able to create a new Timathon"
            },
            {
                "name": "View Timathon Submissions",
                "value": cls.VIEW_TIMATHON_SUBMISSIONS,
                "public": False,
                "help_text": "Users with this permission will be able to view Timathon Submissions"
            },
            {
                "name": "Kick Timathon Participants",
                "value": cls.KICK_TIMATHON_PARTICIPANTS,
                "public": False,
                "help_text": "Users with this permission will be able to kick timathon participants"
            },
            {
                "name": "Ban Timathon Participants",
                "value": cls.BAN_TIMATHON,
                "public": False,
                "help_text": "Users with this permission will be able to ban people "
                             "from participating in timathon"
            },
            {
                "name": "Manage Timathon",
                "value": cls.MANAGE_TIMATHON,
                "public": False,
                "help_text": "Users with this permission will be able to: "
                             "start voting, close timathon...etc"
            }
        ]

        ret = []

        for permission in permissions:
            try:
                if verbose:
                    log.info("Creating permission: " + str(permission))
                permission = await cls.create(**permission)
                ret.append(permission)
            except asyncpg.UniqueViolationError:
                log.error(
                    "Failed to create new permission, UniqueViolationError on permission: "
                    + permission["name"]
                )
                continue

        return ret

    ADMINISTRATOR = 0
    MANAGE_ROLES = 1

    # Timathon Related Permissions
    CREATE_TIMATHON = 2
    VIEW_TIMATHON_SUBMISSIONS = 3
    KICK_TIMATHON_PARTICIPANTS = 4
    BAN_TIMATHON = 5
    MANAGE_TIMATHON = 6
