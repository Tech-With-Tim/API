from datetime import datetime
import pytest

from utils import snowflake_time


EXAMPLE_INTERNAL_ID = 6802059911472611845
EXAMPLE_DISCORD_ID = 144112966176997376
INVALID_ID = 144112966175


@pytest.mark.parametrize(
    "test_id,is_internal,expected",
    [
        (EXAMPLE_DISCORD_ID, False, datetime(2016, 2, 2, 16, 13, 28, 626000)),
        (EXAMPLE_DISCORD_ID, True, datetime(1971, 2, 21, 7, 17, 47, 826000)),
        (EXAMPLE_INTERNAL_ID, True, datetime(2021, 6, 10, 17, 41, 58, 257000)),
        (EXAMPLE_INTERNAL_ID, False, datetime(2066, 5, 23, 2, 37, 39, 57000)),
        (INVALID_ID, False, datetime(2015, 1, 1, 0, 0, 34, 359000)),
        (0, False, datetime(2015, 1, 1, 0, 0)),
        (-INVALID_ID, False, datetime(2014, 12, 31, 23, 59, 25, 640000)),
    ],
)
def test_snowflake_time(test_id, is_internal, expected):
    """
    :param test_id:         Example Snowflake ID
    :param is_internal:     Internal or Discord ID
    :param expected:        Expected datetime
    """
    actual = snowflake_time(id=test_id, internal=is_internal)
    assert expected == actual
