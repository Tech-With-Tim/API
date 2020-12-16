from quart import Response, request, jsonify
from logging import getLogger
from typing import Optional

from .. import blueprint
from api.models import Guild
import utils

request: utils.Request
logger = getLogger("/logs")
NoneType = type(None)


@blueprint.route("/<int:guild_id>", methods=["GET"])
@utils.auth_required
async def fetch_guild(guild_id: int):
    """Fetch `Guild` instance by log ID."""
    guild = await Guild.fetch(id=guild_id)
    if guild is None:
        return jsonify(dict(
            error="404 Not Found",
            message="No Guild with that id in database."
        )), 404

    return jsonify(guild.as_dict())


@blueprint.route('/', methods=["POST"])
@utils.app_only
@utils.expects_data(
    id=int,
    name=str,
    region=str,
    owner_id=int,
    icon_hash=(NoneType, str),
    muted_role_id=(NoneType, Optional[int]),
    log_channel_id=(NoneType, Optional[int]),
    verification_channel_id=(NoneType, Optional[int]),
)
async def create_guild(data: dict):
    """Create a new guild."""
    guild = Guild(**data)

    if not await guild.create():
        return jsonify(dict(
            error="400 Bad Request",
            message="Guild already exists."
        )), 400

    return jsonify(dict(
        message="Guild created."
    )), 201


@blueprint.route('/<int:guild_id>', methods=["PUT"])
async def update_guild(guild_id: int):
    """Update guild with provided kwargs."""

