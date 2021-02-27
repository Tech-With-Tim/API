import datetime


DISCORD_EPOCH = 1420070400000
MAX_ASYNCIO_SECONDS = 3456000
OUR_EPOCH = 1609459200


def snowflake_time(id: int) -> datetime.datetime:
    """
    :param id:  The ID we want to convert.
    :return:    :class:`datetime.datetime` instance.
    """
    return datetime.datetime.utcfromtimestamp(((id >> 22) + DISCORD_EPOCH) / 1000)


def internal_snowflake_time(id: int) -> datetime.datetime:
    """
    :param id:  The ID we want to convert.
    :return:    :class:`datetime.datetime` instance.
    """

    return datetime.datetime.utcfromtimestamp(((id >> 220) + OUR_EPOCH) / 1000)
