import json
import traceback
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
from tqdm import tqdm

from calc_returns import process_sector_pairs
from helpers import parse_timeframe
from sp500 import organize_stocks, sp500_sectors


def get_stock_returns(
    sector: str,
    ticker: str,
    start_date: str,
    end_date: str,
    data_dict: Dict[str, Dict[str, Dict[str, str]]],
) -> None:
    """
    This function calculates the return for a given stock over a given timeframe.

    :param sector: Sector of the stock.
    :param ticker: Stock ticker.
    :param start_date: Start date formatted YYYYMMDD.
    :param end_date: End date formatted YYYYMMDD.
    :param data_dict: Dictionary containing the S&P 500 stocks grouped by sector.
    """
    try:
        df = pd.read_csv(f"./data/{ticker}.csv")

        if len(df) == 0:
            print(f"Issue with stock: {ticker}")
            return

        df = df.set_index("Date")
        df.index = pd.to_datetime(df.index, format="%Y-%m-%d")
        df = df.loc[start_date:end_date]

        initial_price = df["Close"].iloc[0]
        final_price = df["Close"].iloc[-1]
        total_return = (final_price - initial_price) / initial_price * 100

        if (
            total_return > data_dict[sector]["Best"]["Past_Return"]
            or data_dict[sector]["Best"]["Past_Return"] == 0
        ):
            data_dict[sector]["Best"]["Ticker"] = ticker
            data_dict[sector]["Best"]["Past_Return"] = total_return

        if (
            total_return < data_dict[sector]["Worst"]["Past_Return"]
            or data_dict[sector]["Worst"]["Past_Return"] == 0
        ):
            data_dict[sector]["Worst"]["Ticker"] = ticker
            data_dict[sector]["Worst"]["Past_Return"] = total_return
    except:
        print(f"Error with stock: {ticker}")
        print(traceback.format_exc())


def get_sector_pairs(
    start_date: str, timeframe: str, sp500_sectors: Dict[str, List[str]]
) -> Tuple[Dict[str, Dict[str, Dict[str, str]]], datetime]:
    """
    This function calculates the best performing stock and the worst performing stock
    for each sector in the S&P 500 over a given timeframe.

    :param start_date: Start date formatted YYYYMMDD.
    :param timeframe: Timeframe to look past start_date.
    :param sp500_sectors: Dictionary containing the S&P 500 stocks grouped by sector.
    """
    data = {}

    for key in sp500_sectors.keys():
        data[key] = {
            "Best": {"Ticker": "", "Past_Return": 0},
            "Worst": {"Ticker": "", "Past_Return": 0},
        }

    start = datetime.strptime(start_date, "%Y%m%d")

    end = start + parse_timeframe(timeframe)

    for sector in tqdm(sp500_sectors.keys(), desc="Sector Loop", position=0):
        for stock in tqdm(
            sp500_sectors[sector], desc="Stock Loop", position=1, leave=False
        ):
            get_stock_returns(
                sector, stock, start.strftime("%Y%m%d"), end.strftime("%Y%m%d"), data
            )

    return data, end


if __name__ == "__main__":
    sp500_df = sp500_sectors()

    if sp500_df is False:
        print("Failed to scrape S&P 500")
        exit(1)

    sp500_dict = organize_stocks(sp500_df)

    print("Stocks Organized")

    start_date = datetime.strptime("20231012", "%Y%m%d")

    data, end = get_sector_pairs(start_date.strftime("%Y%m%d"), "1y", sp500_dict)

    backtest_end = process_sector_pairs(data, end, "3m")

    total_return = 0

    for sector in data.keys():
        total_return += data[sector]["Best"]["Backtest_Return"]
        total_return += data[sector]["Worst"]["Backtest_Return"]

    print(json.dumps(data, indent=4))

    print(f"Total Return Percentage: {total_return:.2f}%")

    print(f"Start Date: {start_date.strftime("%Y-%m-%d")}")
    print(f"Midpoint: {end.strftime('%Y-%m-%d')}")
    print(f"End Date: {backtest_end.strftime('%Y-%m-%d')}")
