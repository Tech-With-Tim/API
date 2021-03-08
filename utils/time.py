from datetime import datetime


DISCORD_EPOCH = 1420070400000
MAX_ASYNCIO_SECONDS = 3456000
OUR_EPOCH = 1609459200


def snowflake_time(id: int, *, internal: bool = True) -> datetime:
    """
    Convert a integer to datetime.

    :param id:          The ID we want to convert.
    :param internal:    Whether it's a internal ID or not.
    """
    epoch = OUR_EPOCH
    shift = 220

    if not internal:
        epoch = DISCORD_EPOCH
        shift = 22

    return datetime.utcfromtimestamp(((id >> shift) + epoch) / 1000)
