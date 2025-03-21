import re

from dateutil.relativedelta import relativedelta

from .dates import get_row_by_date
from .graphing import (df_to_close_series, import_and_filter_csv,
                       pretty_line_chart)


def parse_timeframe(timeframe: str) -> relativedelta:
    """
    Parses a timeframe argument into a relativedelta object.

    :param timeframe: Timeframe string in the format <number><unit>, e.g. "1d", "2m", "3y".
    :raises ValueError: If the timeframe format is invalid.
    :return:
    """
    timeframe_match = re.search(r"(\d+)(\w+)", timeframe)

    if timeframe_match is None or len(timeframe_match.groups()) != 2:
        raise ValueError("Invalid timeframe format")

    timeframe_amt = int(timeframe_match.group(1))
    timeframe_unit = timeframe_match.group(2)

    delta = relativedelta(days=0)

    if timeframe_unit == "d":
        delta = relativedelta(days=timeframe_amt)
    elif timeframe_unit == "m":
        delta = relativedelta(months=timeframe_amt)
    elif timeframe_unit == "y":
        delta = relativedelta(years=timeframe_amt)

    return delta
