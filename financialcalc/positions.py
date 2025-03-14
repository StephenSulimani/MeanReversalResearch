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


def calculate_position_daily(
    value: float, stock_df: pd.DataFrame, pos_type: PositionType
) -> pd.Series:
    """
    Given a stock's DataFrame and position type, calculate the position's performance, in terms of
    position value every day, represented by a pd.Series indexed by date.

    :param value: The starting capital for the position.
    :param stock_df: The DataFrame representing the stock's historical price.
    :param pos_type: The position type to calculate for.
    :return: pd.Series
    """

    position_value = pd.Series(index=stock_df.index)
    position_value.iloc[0] = value

    stock_original_price = stock_df["Open"].iloc[0]

    if pos_type == PositionType.LONG:
        for i in range(1, len(stock_df)):
            # Calculate the portfolio value each day, WITHOUT compounding.
            position_value.iloc[i] = value * (
                stock_df["Close"].iloc[i] / stock_original_price
            )

    if pos_type == PositionType.SHORT:
        for i in range(1, len(stock_df)):
            # Calculate the portfolio value each day, WITHOUT compounding.
            position_value.iloc[i] = value * (
                stock_original_price / stock_df["Close"].iloc[i]
            )

    return position_value
