from quart import jsonify
from typing import Optional, Union

from api.models import Guild
from .. import bp
import utils


request: utils.Request


@bp.route("", methods=["POST"])
@utils.app_only
@utils.expects_data(
    id=Union[str, int],
    name=str,
    owner_id=Union[str, int],
    icon_hash=Optional[str],
)
async def post_guild(
    id: Union[str, int],
    name: str,
    owner_id: Union[str, int],
    icon_hash: Optional[str] = None,
):
    """Create a guild from the request body"""
    guild = await Guild.create(id, name, owner_id, icon_hash)

    if guild is None:
        # Guild already exists
        return (
            jsonify(
                error="Conflict",
                message=f"Guild with ID {int(id)} already exists.",
            ),
            409,
        )

    return (
        jsonify(
            id=str(guild.id),
            name=guild.name,
            owner_id=str(guild.owner_id),
            icon_hash=guild.icon_hash,
        ),
        201,
        {"Location": f"/guilds/{guild.id}"},
    )


@bp.route("/<int:guild_id>", methods=["GET"])
async def get_guild(guild_id: int):
    """Get a guild from its ID"""
    found, guild, response = await Guild.fetch_or_404(guild_id)
    if not found:
        return response

    return jsonify(
        id=str(guild.id),
        name=guild.name,
        owner_id=str(guild.owner_id),
        icon_hash=guild.icon_hash,
    )


@bp.route("/<int:guild_id>", methods=["PATCH"])
@utils.app_only
@utils.expects_data(
    name=Optional[str],
    owner_id=Optional[Union[str, int]],
    icon_hash=Optional[str],
)
async def patch_guild(guild_id: int, **data):
    """Patch a guild from its ID"""
    found, guild, response = await Guild.fetch_or_404(guild_id)
    if not found:
        return response

    await guild.update(**data)

    return jsonify(
        id=str(guild.id),
        name=guild.name,
        owner_id=str(guild.owner_id),
        icon_hash=guild.icon_hash,
    )


@bp.route("/<int:guild_id>", methods=["DELETE"])
@utils.app_only
async def delete_guild(guild_id: int):
    """Delete a guild from its ID"""
    found, guild, response = await Guild.fetch_or_404(guild_id)
    if not found:
        return response

    await guild.delete()

    return "", 204
