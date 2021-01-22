from quart import jsonify
from typing import Optional, Union, Literal

from api.models import Guild, GuildConfig
from .. import bp
import utils


@bp.route("/<int:guild_id>/config", methods=["POST"])
@utils.app_only
@utils.expects_data(
    xp_enabled=Optional[bool],
    xp_multiplier=Optional[float],
    eco_enabled=Optional[bool],
    muted_role_id=Optional[Union[str, int]],
    do_logging=Optional[bool],
    log_channel_id=Optional[Union[str, int]],
    do_verification=Optional[bool],
    verification_type=Optional[
        Literal[
            "DISCORD_INTEGRATED",
            "DISCORD_CODE",
            "DISCORD_INTEGRATED_CODE",
            "DISCORD_CAPTCHA",
            "DISCORD_INTEGRATED_CAPTCHA",
            "DISCORD_REACTION",
            "DISCORD_INTEGRATED_REACTION",
        ]
    ],
    verification_channel_id=Optional[Union[str, int]],
)
async def post_guild_config(guild_id: int, **data):
    """Create a Config for a guild"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            jsonify(
                error="Not found", message=f"Guild with ID {guild_id} doesn't exist."
            ),
            404,
        )

    try:
        guild_config = await GuildConfig.create(guild_id, **data)
    except ValueError as e:
        return jsonify(error="Bad request", message=str(e) + "."), 400

    if guild_config is None:
        # GuildConfig already exists
        return (
            jsonify(
                error="Conflict",
                message=f"Guild with ID {guild_id} already has a config.",
            ),
            409,
        )

    return (
        jsonify(
            {
                name: str(value)
                if name.endswith("_id") and value is not None
                else value
                for name, value in guild_config.as_dict().items()
            }
        ),
        201,
        {"Location": f"/guilds/{guild.id}/config"},
    )


@bp.route("/<int:guild_id>/config", methods=["GET"])
@utils.app_only
async def get_guild_config(guild_id: int):
    """Get the Config for a guild"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            jsonify(
                error="Not found", message=f"Guild with ID {guild_id} doesn't exist."
            ),
            404,
        )

    guild_config = await GuildConfig.fetch(guild_id)
    if guild_config is None:
        return (
            jsonify(
                error="Not found",
                message=f"Guild with ID {guild_id} doesn't have a configuration.",
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
@utils.app_only
@utils.expects_data(
    xp_enabled=Optional[bool],
    xp_multiplier=Optional[float],
    eco_enabled=Optional[bool],
    muted_role_id=Optional[Union[str, int]],
    do_logging=Optional[bool],
    log_channel_id=Optional[Union[str, int]],
    do_verification=Optional[bool],
    verification_type=Optional[
        Literal[
            "DISCORD_INTEGRATED",
            "DISCORD_CODE",
            "DISCORD_INTEGRATED_CODE",
            "DISCORD_CAPTCHA",
            "DISCORD_INTEGRATED_CAPTCHA",
            "DISCORD_REACTION",
            "DISCORD_INTEGRATED_REACTION",
        ]
    ],
    verification_channel_id=Optional[Union[str, int]],
)
async def patch_guild_config(guild_id: int, **data):
    """Patch the Config for a guild"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            jsonify(
                error="Not found", message=f"Guild with ID {guild_id} doesn't exist."
            ),
            404,
        )

    guild_config = await GuildConfig.fetch(guild_id)
    if guild_config is None:
        return (
            jsonify(
                error="Not found",
                message=f"Guild with ID {guild_id} doesn't have a configuration.",
            ),
            404,
        )

    await guild_config.update(**data)

    return jsonify(
        {
            name: str(value) if name.endswith("_id") and value is not None else value
            for name, value in guild_config.as_dict().items()
        }
    )


@bp.route("/<int:guild_id>/config", methods=["DELETE"])
@utils.app_only
async def delete_guild_config(guild_id: int):
    """Delete the Config for a guild"""
    guild = await Guild.fetch(guild_id)
    if guild is None:
        return (
            jsonify(
                error="Not found", message=f"Guild with ID {guild_id} doesn't exist."
            ),
            404,
        )

    guild_config = await GuildConfig.fetch(guild_id)
    if guild_config is None:
        return (
            jsonify(
                error="Not found",
                message=f"Guild with ID {guild_id} doesn't have a configuration.",
            ),
            404,
        )

    await guild_config.delete()

    return "", 204
