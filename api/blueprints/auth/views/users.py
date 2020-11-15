from quart import Response, request, jsonify
from utils import Request, auth_required

from .. import blueprint

request: Request


@blueprint.route('/users/@me', methods=["GET"])
@auth_required
async def get_user() -> Response:
    """
    Returns the `User` object of the requester's account.

    Requires Token authentication.
    """
    return jsonify(request.user.as_json())
