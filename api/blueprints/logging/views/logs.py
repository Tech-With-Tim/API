from quart import Response, request, jsonify
from logging import getLogger

from .. import blueprint
from api.models import Log
import utils

request: utils.Request
logger = getLogger("/logs")


@blueprint.route("/<int:log_id>", methods=["GET"])
async def fetch_log(log_id: int):
    """Fetch `Log` instance by log ID."""
    log = await Log.fetch(id=log_id)

    if log is None:
        return jsonify({"error": "404 Not Found - No log with that id in database."}), 404

    return jsonify(log.as_dict())


@blueprint.route("/", methods=["POST"])
@utils.auth_required
@utils.expects_data(
    type=str,
    data=dict
)
async def create_log(data: dict):
    """Create a new Log instance."""
    await Log(type=data["type"], data=data["data"]).create()
    return Response("", 201)
