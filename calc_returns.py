import json
from datetime import datetime
from typing import Dict

import pandas as pd

from helpers import parse_timeframe


def calc_short_return(ticker, start_date, end_date):
    """
    Function to calculate the return of a short stock trade in percentage terms.
    """
    # Download stock data
    # Uses data already downloaded, change this line to make it dynamic.
    stock = pd.read_csv(f"./data/{ticker}.csv")
    stock = stock.set_index("Date")

    stock.index = pd.to_datetime(stock.index, format="%Y-%m-%d")

    stock = stock.loc[start_date:end_date]

    # Ensure data is available
    if stock.empty:
        print("No data available for the given date range.")
        return None

    # Select short and cover dates (first & last available trading days)
    short_date = stock.index[0]  # First trading day
    cover_date = stock.index[-1]  # Last trading day

    # Get stock prices
    short_price = stock.loc[short_date, "Open"]
    cover_price = stock.loc[cover_date, "Close"]

    # Calculate Short Return as a Percentage
    percent_return = ((short_price - cover_price) / short_price) * 100

    # Display results
    result = {
        "Short Date": short_date.date(),
        "Short Price ($)": round(short_price, 2),
        "Cover Date": cover_date.date(),
        "Cover Price ($)": round(cover_price, 2),
        "Short Return (%)": round(percent_return, 2),
    }

    # for key, value in result.items():
    #    print(f"\t{key}: {value}")

    return percent_return


def calc_long_return(ticker, start_date, end_date):
    """
    Function to calculate the return of a long stock trade in percentage terms.
    """
    # Download stock data
    # Uses data already downloaded, change this line to make it dynamic.
    stock = pd.read_csv(f"./data/{ticker}.csv")

    stock = stock.set_index("Date")
    stock.index = pd.to_datetime(stock.index, format="%Y-%m-%d")
    stock = stock.loc[start_date:end_date]

    # Ensure data is available
    if stock.empty:
        print("No data available for the given date range.")
        return None

    # Select short and cover dates (first & last available trading days)
    buy_date = stock.index[0]  # First trading day
    sell_date = stock.index[-1]  # Last trading day

    # Get stock prices
    buy_price = stock.loc[buy_date, "Open"]
    sell_price = stock.loc[sell_date, "Close"]

    # Calculate Short Return as a Percentage
    percent_return = ((sell_price - buy_price) / buy_price) * 100

    # Plot stock price
    # plot_stock_price(stock, short_date, cover_date, short_price, cover_price)

    # Display results
    result = {
        "Buy Date": buy_date.date(),
        "Buy Price ($)": round(buy_price, 2),
        "Sell Date": sell_date.date(),
        "Sell Price ($)": round(sell_price, 2),
        "Long Return (%)": round(percent_return, 2),
    }

    # for key, value in result.items():
    #    print(f"\t{key}: {value}")

    return percent_return


# WORK IN PROGRESS!!!! WORK IN PROGRESS!!!!
# def eleven_pairs(best_worst_pairs: dict, start_date: str, end_date: str):
def eleven_pairs():
    """
    Finds the returns of the best and worst pair for each "GICS"
    identified sector in the S&P 500 over a given time frame for
    testing.
    :param start_date: The start date.
    :param end_date: The end date.
    :return: None (for RIGHT NOW)
    """

    with open("sample_sector_pairs.json", "r") as json_file:
        sample_sector_pairs = json.load(json_file)

    print(f"The type of sample_sector_pairs is: " f"{type(sample_sector_pairs)}")

    # Accessing the first sector (e.g., "Industrials") and its stock list
    first_sector = list(sample_sector_pairs.keys())[
        0
    ]  # This gets the first sector name
    print(
        f"\n\nstocks_by_sector[{first_sector}] is:\n"
        f" {sample_sector_pairs[first_sector]}"
    )


def process_sector_pairs(sector_pairs: Dict, start_date: datetime, timeframe: str):
    """
    This function tests the best and worst performing stocks with short and long positions,
    respectively over a given timeframe and returns the results.

    :param sector_pairs:
    :param start_date:
    :param end_date:
    """
    end_date = start_date + parse_timeframe(timeframe)
    for sector in sector_pairs.keys():
        sector_pairs[sector]["Best"]["Backtest_Return"] = calc_short_return(
            sector_pairs[sector]["Best"]["Ticker"], start_date, end_date
        )
        sector_pairs[sector]["Worst"]["Backtest_Return"] = calc_long_return(
            sector_pairs[sector]["Worst"]["Ticker"], start_date, end_date
        )

    return end_date


# Example usage
if __name__ == "__main__":
    # short_stock_return("AAPL", "2023-08-13", "2024-02-13")
    print("Example Usage:")
    # print("Short on AAPL from 2023-08-13 to 2024-02-13")
    # calc_short_return("AAPL", "20230813", "20240213")
    # print("\nLong on GOOG from 2023-08-13 to 2024-02-13")
    # calc_long_return("GOOG", "20230813", "20240213")
    print("calling eleven_pairs")
    eleven_pairs()
