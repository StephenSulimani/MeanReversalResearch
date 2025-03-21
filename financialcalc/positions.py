from enum import Enum, auto

import pandas as pd


class PositionType(Enum):
    LONG = auto()
    SHORT = auto()


def calculate_position(stock_df: pd.DataFrame, pos_type: PositionType) -> float:
    """Calculate the return of a position based on the provided stock DataFrame and position type.

    This function computes the position's return and returns it as a float.

    Args:
        stock_df (pd.DataFrame): A DataFrame containing the stock's historical price data.
        pos_type (str): The type of position to calculate (e.g., long, short).

    Returns:
        float: The calculated return of the position.
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
    """Calculate the position's performance based on the provided stock DataFrame and position type.

    This function computes the daily position value and returns a pd.Series indexed by date that reflects the performance of the position.

    Args:
        value (float): The starting capital for the position.
        stock_df (pd.DataFrame): A DataFrame containing the stock's historical price data.
        pos_type (str): The type of position to calculate (e.g., long, short).

    Returns:
        pd.Series: A Series representing the position's value for each day, indexed by date.
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
