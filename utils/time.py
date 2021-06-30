import datetime


DISCORD_EPOCH = 1420070400000
MAX_ASYNCIO_SECONDS = 3456000
OUR_EPOCH = 1609459200


def snowflake_time(id: int, *, internal: bool = True) -> datetime.datetime:
    """
    :param id:          The ID we want to convert.
    :param internal:    Whether it's a internal ID or not.

    :return:            :class:`datetime.datetime` instance.
    """

    epoch = OUR_EPOCH

    if not internal:
        epoch = DISCORD_EPOCH

    return datetime.datetime.utcfromtimestamp(((id >> 22) + epoch) / 1000)
