from api.models import Asset
from quart import current_app, Response, jsonify
import utils
from .. import blueprint


@blueprint.route("/cdn", methods=["POST"])
@utils.expects_data(
    name=str,
    type=(str),
    base64=(str)
)
async def create_asset(data: dict):
    name = data["name"]
    type = data["type"]
    base64 = data["base64"]
    if type and name and base64 != "":
        db_uri = name + type + base64
        asset = Asset(name=data["name"],
                      type=data["type"],
                      base64=data["base64"],
                      url_path=db_uri)
        created = await asset.create()
        return Response("", status=202 - created)

    return (
        jsonify(
            {
                "error": "400 Bad Request One or more field missing",
            }
        ), 400)


@blueprint.route("/cdn/<str:url_path>", methods=["GET"])
async def load_asset(url_path: str):
    load = await current_app.db.fetch_user(url_path=url_path)

    if load is None:
        return(jsonify(
                {
                    "error": "404 Not Found - The requested asset could not be found in our database."
                }
            ),
            404,
        )
    return jsonify(load.as_dict(load))
# asset1 = Asset(name="Badge 1", url_path="badge1", type="Badge", data=open("image.png"))
