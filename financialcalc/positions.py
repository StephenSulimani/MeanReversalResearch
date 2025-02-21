from enum import Enum, auto

import pandas as pd


class PositionType(Enum):
    LONG = auto()
    SHORT = auto()


def calculate_position(stock_df: pd.DataFrame, pos_type: PositionType) -> float:
    """
    Given a stock's DataFrame and position type, calculate the positon's
    return as a float.

    :param stock_df: The DataFrame representing the stock's historical price.
    :param pos_type: The position type to calculate for.
    :return: float
    """
    first_day = stock_df["Open"].iloc[0]
    last_day = stock_df["Close"].iloc[-1]

    if pos_type == PositionType.LONG:
        return ((last_day - first_day) / first_day) * 100

    if pos_type == PositionType.SHORT:
        return ((first_day - last_day) / first_day) * 100

    return -999.99
