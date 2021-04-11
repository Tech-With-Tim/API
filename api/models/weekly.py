from postDB import Model, Column, types
from typing import Optional, Union
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
    created_by = Column(
        types.ForeignKey("users", "id", sql_type=types.Integer(big=True))
    )
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
    async def update(cls, weekly_challenge_id: int = None, **data):
        """Update Role Data"""
        update_query = ["UPDATE challenges SET"]

        fields = (
            "title",
            "description",
            "examples",
            "rules",
            "difficulty",
        )
        new_data = {field: data[field] for field in fields if field in data.keys()}

        if len(new_data) > 0:
            update_query.append(
                ", ".join(
                    "%s = $%d" % (key, i) for i, key in enumerate(new_data.keys(), 2)
                )
            )

            update_query.append("WHERE challenges.id = $1 RETURNING *;")

            query = " ".join(update_query)
            record = await cls.pool.fetchrow(
                query,
                int(weekly_challenge_id),
                *new_data.values(),
            )

            if record is None:
                return None

            for field, value in record.items():
                setattr(cls, field, value)

        return cls

    @classmethod
    async def delete(cls, id) -> Optional["Challenge"]:
        """Deletes the Challenge."""

        query = """
        DELETE FROM challenges
        WHERE id = $1
        RETURNING *;
        """
        record = await cls.pool.fetchrow(query, int(id))

        if record is None:
            return None

        for field, value in record.items():
            setattr(cls, field, value)

    @property
    def created_at(self) -> datetime:
        return utils.snowflake_time(self.id)
