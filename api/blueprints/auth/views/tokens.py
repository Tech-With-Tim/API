from quart import current_app, Response, request, jsonify

import time

from utils import Request, auth_required, expects_data
from .. import blueprint

from db.models import User

request: Request


@blueprint.route('/tokens/@me', methods=["GET"])
async def get_my_token():
    pass