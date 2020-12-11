from quart import current_app, Response, request, jsonify, send_file
from logging import getLogger
import asyncpg


from .. import blueprint
from api.models import User, Asset
import utils

request: utils.Request
log = getLogger("/cdn")


@blueprint.route('/manage/create', methods=["GET"])
@utils.auth_required
@utils.expects_form_data(name=str, url_path=str, type=str)
@utils.expects_files("data")
async def create_asset(data: dict, files: dict):
    """
    Create a Asset object.

    Returns status 202 if a new asset was not created, 201 if a new asset was created.
    # TODO: Require a given group to do this.
    """
    try:
        asset = Asset(
            name=data["name"],
            url_path=data["url_path"],
            type=data["type"],
            mimetype=files["data"].mimetype,
            data=files["data"].stream
        )
        await asset.create()
    except asyncpg.UniqueViolationError:
        return jsonify({
            "error": "403 Forbidden - Asset with this name or url_path already exists."
        })

    return Response("", status=201)


@blueprint.route('/<path>', methods=["GET"])
async def fetch_asset(path: str):
    """Default GET endpoint for assets."""
    asset = await Asset.fetch(url_path=path)

    if asset is None:
        return jsonify({"error": "NotFound - Nothing matches the given URI", "ok": "boomer"}), 404
    else:
        return await send_file(asset.data, mimetype=asset.mimetype)
