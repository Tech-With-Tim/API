from quart import request, redirect, jsonify

from api.models import Guild
from .. import bp
import utils


request: utils.Request
GUILD_COLUMNS = {column.name for column in Guild.columns} - {"icon_hash"}


@bp.route("", methods=["POST"])
async def create_guild():
    """Create a guild from the request body"""
    data: dict = await request.json or {}
    if not all(c in data for c in GUILD_COLUMNS):
        # Missing data
        return (
            {
                "error": "Bad Request",
                "message": f"Missing {', '.join(GUILD_COLUMNS - set(data))} in JSON data.",
            },
            400,
        )
    guild = await Guild.create(
        data["id"], data["name"], data["owner_id"], data.get("icon_hash", None)
    )

    if guild is None:
        # Guild already exists
        return (
            {
                "error": "Conflict",
                "message": f"Guild with ID {int(data['id'])} already exists.",
            },
            409,
        )

    response = jsonify(
        {
            "id": str(guild.id),
            "name": guild.name,
            "owner_id": str(guild.owner_id),
            "icon_hash": guild.icon_hash,
        }
    )
    response.headers.add("Location", f"/guilds/{guild.id}")

    return (
        response,
        201,
    )


@bp.route("/<int:guild_id>", methods=["GET", "PATCH", "DELETE"])
async def guild(guild_id):
    """Get a guild from its ID"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            {
                "error": "Not found",
                "message": f"Guild with ID {guild_id} doesn't exist.",
            },
            404,
        )

    if request.method == "PATCH":
        data = await request.json or {}
        await guild.update(**data)

    elif request.method == "DELETE":
        await guild.delete()

    return {
        "id": str(guild.id),
        "name": guild.name,
        "owner_id": str(guild.owner_id),
        "icon_hash": guild.icon_hash,
    }


@bp.route("/<int:guild_id>/icon", methods=["GET"])
async def guild_icon(guild_id):
    """Get a guild icon from its ID"""
    guild = await Guild.fetch(guild_id)

    format = request.args.get("format", None)
    static_format = request.args.get("static_format", "webp")
    try:
        size = int(request.args.get("size", 128))
    except ValueError:
        return (
            {
                "error": "Bad Request",
                "message": "size needs to be an integer.",
            },
            400,
        )

    try:
        url = guild.icon_url_as(
            format=format,
            static_format=static_format,
            size=size,
        )
    except ValueError as e:
        return (
            {
                "error": "Bad Request",
                "message": str(e) + ".",
            },
            400,
        )

    return redirect(url)
