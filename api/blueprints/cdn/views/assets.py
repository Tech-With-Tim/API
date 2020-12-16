from quart import Response, request, jsonify, send_file
from logging import getLogger
import io

from .. import blueprint
from api.models import User, Asset
import utils

request: utils.Request
log = getLogger("/cdn")


@blueprint.route("/manage", methods=["POST"])
@utils.auth_required
@utils.expects_form_data(name=str, url_path=str, type=str)
@utils.expects_files("data")
async def create_asset(data: dict, files: dict):
    """
    Create a Asset object.

    Returns status 202 if a new asset was not created, 201 if a new asset was created.
    # TODO: Require a given group to do this.
    """
    asset = Asset(
        name=data["name"],
        url_path=data["url_path"],
        type=data["type"],
        mimetype=files["data"].mimetype,
        data=files["data"].stream,
    )

    if await asset.create():
        return jsonify(asset.as_dict("id", "name", "url_path", "type", "mimetype")), 201
    else:
        return (
            jsonify(
                {
                    "error": "403 Forbidden - Asset with this name or url_path already exists."
                }
            ),
            403,
        )


@blueprint.route("/manage/<int:asset_id>", methods=["POST"])
@utils.expects_form_data(name=str, url_path=str, type=str)
@utils.auth_required
async def edit_asset(data: dict, asset_id: int):
    """
    Edit asset by asset ID.

    TODO: Require a given group to do this.
    """

    asset = await Asset.fetch(id=asset_id)
    if asset is None:
        return (
            jsonify({"error": "404 Not Found - No asset with that ID in database."}),
            404,
        )

    files = await request.files
    if (file := files.get("data")) is not None:
        asset.mimetype = file.mimetype
        asset.data = file.stream

    for arg in ("name", "url_path", "type"):
        if (value := data.get(arg)) is not None:
            setattr(asset, arg, value)

    if await asset.save():
        return Response("", status=204)

    return (
        jsonify(
            {
                "error": "403 Forbidden - Asset with this name or url_path already exists."
            }
        ),
        403,
    )


@blueprint.route("/manage/<int:asset_id>", methods=["DELETE"])
@utils.auth_required
async def delete_asset(asset_id: int):
    """
    Delete asset by asset ID.
    """
    record = await Asset.delete(asset_id=asset_id)

    cnt = int(record[-1])

    if cnt == 0:
        return (
            jsonify({"error": "404 Not Found - No asset with that ID in database."}),
            404,
        )

    return jsonify({"messages": record})


@blueprint.route("/manage/<path>", methods=["GET"])
async def info_asset(path: str):
    """
    GET information about a given asset.

    path can be either the url_path or id attribute.
    """
    if path.isdigit():
        query = {"id": int(path)}
    else:
        query = {"url_path": path}

    asset = await Asset.fetch(**query)

    if asset is None:
        return (
            jsonify(
                {
                    "error": "404 Not Found - No asset with that {} in database.".format(
                        list(query)[0]
                    )
                }
            ),
            404,
        )

    return jsonify(asset.as_dict("id", "name", "url_path", "type", "mimetype"))


@blueprint.route("/<path>", methods=["GET"])
async def fetch_asset(path: str):
    """Default GET endpoint for assets."""
    asset = await Asset.fetch(url_path=path)

    if asset is None:
        return jsonify({"error": "NotFound - Nothing matches the given URI"}), 404

    return await send_file(io.BytesIO(asset.data), mimetype=asset.mimetype)
