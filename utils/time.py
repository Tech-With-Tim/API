import datetime
import asyncio


DISCORD_EPOCH = 1420070400000
MAX_ASYNCIO_SECONDS = 3456000


def snowflake_time(id):
    """
    Parameters
    -----------
    id: :class:`int`
        The snowflake ID.
    Returns
    --------
    :class:`datetime.datetime`
        The creation date in UTC of a Discord snowflake ID."""
    return datetime.datetime.utcfromtimestamp(((id >> 22) + DISCORD_EPOCH) / 1000)


async def sleep_until(when, result=None):
    """|coro|
    Sleep until a specified time.
    If the time supplied is in the past this function will yield instantly.
    .. versionadded:: 1.3
    Parameters
    -----------
    when: :class:`datetime.datetime`
        The timestamp in which to sleep until. If the datetime is naive then
        it is assumed to be in UTC.
    result: Any
        If provided is returned to the caller when the coroutine completes.
    """
    if when.tzinfo is None:
        when = when.replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)
    delta = (when - now).total_seconds()
    while delta > MAX_ASYNCIO_SECONDS:
        await asyncio.sleep(MAX_ASYNCIO_SECONDS)
        delta -= MAX_ASYNCIO_SECONDS
    return await asyncio.sleep(max(delta, 0), result)
