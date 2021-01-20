from quart import request, redirect, jsonify

from api.models import Guild, GuildConfig
from .. import bp
import utils


request: utils.Request
GUILD_COLUMNS = {column.name for column in Guild.columns} - {"icon_hash"}
GUILD_CONFIG_COLUMNS = {column.name for column in GuildConfig.columns} - {"guild_id"}


@bp.route("", methods=["POST"])
async def post_guild():
    """Create a guild from the request body"""
    data: dict = await request.json or {}
    if not all(c in data for c in GUILD_COLUMNS):
        # Missing data
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": f"Missing {', '.join(GUILD_COLUMNS - set(data))} in JSON data.",
                }
            ),
            400,
        )
    guild = await Guild.create(
        data["id"], data["name"], data["owner_id"], data.get("icon_hash", None)
    )

    if guild is None:
        # Guild already exists
        return (
            jsonify(
                {
                    "error": "Conflict",
                    "message": f"Guild with ID {int(data['id'])} already exists.",
                }
            ),
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


@bp.route("/<int:guild_id>", methods=["GET"])
async def get_guild(guild_id: int):
    """Get a guild from its ID"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            jsonify(
                {
                    "error": "Not found",
                    "message": f"Guild with ID {guild_id} doesn't exist.",
                }
            ),
            404,
        )

    return jsonify(
        {
            "id": str(guild.id),
            "name": guild.name,
            "owner_id": str(guild.owner_id),
            "icon_hash": guild.icon_hash,
        }
    )


@bp.route("/<int:guild_id>", methods=["PATCH"])
async def patch_guild(guild_id: int):
    """Patch a guild from its ID"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            jsonify(
                {
                    "error": "Not found",
                    "message": f"Guild with ID {guild_id} doesn't exist.",
                }
            ),
            404,
        )

    data = await request.json or {}
    await guild.update(**data)

    return jsonify(
        {
            "id": str(guild.id),
            "name": guild.name,
            "owner_id": str(guild.owner_id),
            "icon_hash": guild.icon_hash,
        }
    )


@bp.route("/<int:guild_id>", methods=["DELETE"])
async def delete_guild(guild_id: int):
    """Delete a guild from its ID"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            jsonify(
                {
                    "error": "Not found",
                    "message": f"Guild with ID {guild_id} doesn't exist.",
                }
            ),
            404,
        )

    await guild.delete()

    return jsonify(
        {
            "id": str(guild.id),
            "name": guild.name,
            "owner_id": str(guild.owner_id),
            "icon_hash": guild.icon_hash,
        }
    )


@bp.route("/<int:guild_id>/icon", methods=["GET"])
async def get_guild_icon(guild_id: int):
    """Get a guild icon from its ID"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            jsonify(
                {
                    "error": "Not found",
                    "message": f"Guild with ID {guild_id} doesn't exist.",
                }
            ),
            404,
        )

    format = request.args.get("format", None)
    static_format = request.args.get("static_format", "webp")
    try:
        size = int(request.args.get("size", 128))
    except ValueError:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "size needs to be an integer.",
                }
            ),
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
            jsonify(
                {
                    "error": "Bad Request",
                    "message": str(e) + ".",
                }
            ),
            400,
        )

    return redirect(url)


@bp.route("/<int:guild_id>/config", methods=["POST"])
async def post_guild_config(guild_id: int):
    """Create a Config for a guild"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            jsonify(
                {
                    "error": "Not found",
                    "message": f"Guild with ID {guild_id} doesn't exist.",
                }
            ),
            404,
        )

    data: dict = await request.json or {}
    data = {name: value for name, value in data.items() if name in GUILD_CONFIG_COLUMNS}
    try:
        guild_config = await GuildConfig.create(guild_id, **data)
    except ValueError as e:
        return jsonify({"error": "Bad request", "message": str(e) + "."}), 400

    if guild_config is None:
        # GuildConfig already exists
        return (
            jsonify(
                {
                    "error": "Conflict",
                    "message": f"Guild with ID {guild_id} already has a config.",
                }
            ),
            409,
        )

    response = jsonify(
        {
            name: str(value) if name.endswith("_id") and value is not None else value
            for name, value in guild_config.as_dict().items()
        }
    )

    response.headers.add("Location", f"/guilds/{guild.id}/config")

    return (
        response,
        201,
    )


@bp.route("/<int:guild_id>/config", methods=["GET"])
async def get_guild_config(guild_id: int):
    """Get the Config for a guild"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            jsonify(
                {
                    "error": "Not found",
                    "message": f"Guild with ID {guild_id} doesn't exist.",
                }
            ),
            404,
        )

    guild_config = await GuildConfig.fetch(guild_id)
    if guild_config is None:
        return (
            jsonify(
                {
                    "error": "Not found",
                    "message": f"Guild with ID {guild_id} doesn't have a Config.",
                }
            ),
            404,
        )

    return jsonify(
        {
            name: str(value) if name.endswith("_id") and value is not None else value
            for name, value in guild_config.as_dict().items()
        }
    )


@bp.route("/<int:guild_id>/config", methods=["PATCH"])
async def patch_guild_config(guild_id: int):
    """Patch the Config for a guild"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            jsonify(
                {
                    "error": "Not found",
                    "message": f"Guild with ID {guild_id} doesn't exist.",
                }
            ),
            404,
        )

    guild_config = await GuildConfig.fetch(guild_id)
    if guild_config is None:
        return (
            jsonify(
                {
                    "error": "Not found",
                    "message": f"Guild with ID {guild_id} doesn't have a Config.",
                }
            ),
            404,
        )

    data = await request.json or {}
    try:
        await guild_config.update(**data)
    except ValueError as e:
        return jsonify({"error": "Bad request", "message": str(e) + "."}), 400

    return jsonify(
        {
            name: str(value) if name.endswith("_id") and value is not None else value
            for name, value in guild_config.as_dict().items()
        }
    )


@bp.route("/<int:guild_id>/config", methods=["DELETE"])
async def delete_guild_config(guild_id: int):
    """Delete the Config for a guild"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            jsonify(
                {
                    "error": "Not found",
                    "message": f"Guild with ID {guild_id} doesn't exist.",
                }
            ),
            404,
        )

    guild_config = await GuildConfig.fetch(guild_id)
    if guild_config is None:
        return (
            jsonify(
                {
                    "error": "Not found",
                    "message": f"Guild with ID {guild_id} doesn't have a Config.",
                }
            ),
            404,
        )

    await guild_config.delete()

    return jsonify(
        {
            name: str(value) if name.endswith("_id") and value is not None else value
            for name, value in guild_config.as_dict().items()
        }
    )
