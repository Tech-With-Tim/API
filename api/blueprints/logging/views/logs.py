from quart import Response, request, jsonify, send_file
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
