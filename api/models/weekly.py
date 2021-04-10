from postDB import Model, Column, types
from typing import Optional, Union
from http import HTTPStatus
from quart import exceptions
from datetime import datetime
import utils


class Challenge(Model):
    """
    Weekly Challenges model for storing information about weekly challenges.

    :param int id:                   The challenge id.
    :param str title:                The challenge title.
    :param int description:          The challenge description.
    :param str example:              The challenge examples.
    :param str rule:                 The challenge rules.
    :param str created_by:           The challenge creator.

    """

    id = Column(types.Integer(big=True), primary_key=True)
    title = Column(types.String())
    description = Column(types.String())
    examples = Column(types.String())
    rules = Column(types.String())
    created_by = Column(types.String())
    difficulty = Column(types.String())

    @classmethod
    async def create(
        cls,
        id: Union[str, int],
        title: str,
        description: str,
        examples: str,
        rules: str,
        created_by: str,
        difficulty: str,
    ) -> Optional["Challenge"]:
        """
        Creates a new Weekly challenge.

        Returns the new challenge if created.
        Returns `None` if a Unique Violation occurred.
        """
        query = """
           INSERT INTO challenges (id, title, description, examples, rules, created_by, difficulty)
           VALUES ($1, $2, $3, $4, $5, $6, $7)
           ON CONFLICT DO NOTHING
           RETURNING *;
           """

        record = await cls.pool.fetchrow(
            query, int(id), title, description, examples, rules, created_by, difficulty
        )

        if record is None:
            return None

        return cls(**record)

    @classmethod
    async def fetch(cls, id: Union[str, int]) -> Optional["Challenge"]:
        """Fetch a weekly challenge with the given ID."""
        query = "SELECT * FROM challenges WHERE id = $1"
        record = await cls.pool.fetchrow(query, int(id))

        if record is None:
            return None

        return cls(**record)

    @classmethod
    async def fetch_or_404(cls, id: Union[str, int]) -> Optional["Challenge"]:
        """
        Fetch a weekly challenge with the given ID or send a 404 error.

        :param Union[str, int] weekly_challenge: The weekly challenge's id.
        """

        if challenge := await cls.fetch(id):
            return challenge

        http_status = HTTPStatus.NOT_FOUND
        http_status.description = f"The weekly challenge with ID {id} doesn't exist."
        raise exceptions.NotFound(http_status)

    async def update(self, **fields) -> Optional["Challenge"]:
        """Update the Challenge with the given arguments."""

        if not fields:
            return self

        allowed_fields = (
            "title",
            "description",
            "examples",
            "rules",
            "created_by",
            "difficulty",
        )
        fields = {
            name: fields.get(name, getattr(self, name)) for name in allowed_fields
        }

        query = """
           UPDATE challenges
           SET
               title = $2,
               description = $3,
               examples = $4,
               rules = $5,
               created_by = $6,
               difficulty = $7
           WHERE id = $1
           RETURNING *;
           """
        record = await self.pool.fetchrow(
            query,
            int(self.id),
            fields["title"],
            fields["description"],
            fields["examples"],
            fields["rules"],
            fields["created_by"],
            fields["difficulty"],
        )

        if record is None:
            return None

        for field, value in record.items():
            setattr(self, field, value)

        return self

    async def delete(self) -> Optional["Challenge"]:
        """Deletes the Challenge."""

        query = """
        DELETE FROM challenges
        WHERE id = $1
        RETURNING *;
        """
        record = await self.pool.fetchrow(query, int(self.id))

        if record is None:
            return None

        for field, value in record.items():
            setattr(self, field, value)

        return self

    @property
    def created_at(self) -> datetime:
        return utils.snowflake_time(self.id)
