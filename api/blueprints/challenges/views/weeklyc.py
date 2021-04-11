from quart import jsonify, request
from api.models import Challenge
from .. import bp
import utils
from typing import Union, Optional

request: utils.Request


@bp.route("/weekly", methods=["POST"])
@utils.auth_required
@utils.expects_data(
    id=Union[str, int],
    title=str,
    description=str,
    examples=str,
    rules=str,
    difficulty=str,
)
async def post_challenge(
    id: Union[str, int],
    title: str,
    description: str,
    examples: str,
    rules: str,
    difficulty: str,
):
    created_by = request.user_id
    challenge = await Challenge.create(
        id, title, description, examples, rules, created_by, difficulty
    )

    if challenge is None:
        # Challenge already exists
        return (
            jsonify(
                error="Conflict",
                message=f"Challenge with ID {int(id)} already exists.",
            ),
            409,
        )

    return (
        jsonify(
            id=str(challenge.id),
            title=challenge.title,
            description=str(challenge.description),
            examples=challenge.examples,
            rules=challenge.rules,
            created_by=challenge.created_by,
            difficulty=challenge.difficulty,
        ),
        201,
        {"Location": f"/challenges/weekly/{challenge.id}"},
    )


@bp.route("/weekly/<int:weekly_challenge_id>", methods=["GET"])
async def get_challenge(weekly_challenge_id: int):
    """Gets the Weekly Challenge"""

    challenge = await Challenge.fetch(weekly_challenge_id)

    if challenge is None:
        return (
            jsonify(
                error="Not Found",
                message=f"Challenge with ID {int(weekly_challenge_id)} doesn't exists.",
            ),
            404,
        )
    return jsonify(
        id=str(challenge.id),
        title=challenge.title,
        description=str(challenge.description),
        examples=challenge.examples,
        rules=challenge.rules,
        created_by=str(challenge.created_by),
        difficulty=challenge.difficulty,
    )


@bp.route("/weekly/<int:weekly_challenge_id>", methods=["PATCH"])
@utils.expects_data(
    title=Optional[str],
    description=Optional[str],
    examples=Optional[str],
    rules=Optional[str],
    difficulty=Optional[str],
)
async def update_challenge(weekly_challenge_id: int, **data):
    """Update a weekly challenge from its ID"""
    await Challenge.update(weekly_challenge_id=weekly_challenge_id, **data)

    return jsonify(**data)


@bp.route("/weekly/<int:weekly_challenge_id>", methods=["DELETE"])
@utils.auth_required
async def delete_challenge(weekly_challenge_id: int):
    """Deletes a challenge from its ID"""

    await Challenge.delete(weekly_challenge_id)
    return jsonify("Challenge Deleted", 204)
