from quart import Response, request, jsonify
from logging import getLogger

from .. import blueprint
from api.models import Guild
import utils

request: utils.Request
logger = getLogger("/logs")


@blueprint.route("/<int:guild_id>", methods=["GET"])
@utils.auth_required
async def fetch_guild(guild_id: int):
    """Fetch `Guild` instance by log ID."""
    guild = await Guild.fetch(id=guild_id)
    if guild is None:
        return jsonify({"error": "404 Not Found - No Guild with that id in database."}), 404

    return jsonify(guild.as_dict())


@blueprint.route('/', methods=["POST"])
@utils.auth_required  # TODO -> app_only
@utils.expects_data()
async def create_guild(data: dict):
    """Create a new guild."""
    pass
