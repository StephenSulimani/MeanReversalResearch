import re
import traceback
from datetime import datetime
from multiprocessing.pool import ThreadPool
from threading import Lock
from typing import Dict, List, Literal, Tuple

import pandas as pd
import requests
from tqdm import tqdm

from helpers import parse_timeframe
from macrotrends import MacroTrends
from stooq import Stooq


def sp500_sectors() -> pd.DataFrame | Literal[False]:
    """
    This function scrapes the S&P 500 stocks from the Wikiepedia page,
    and creates a DataFrame containing each stock's ticker, company name,
    and GICS Sector.

    :return: A DataFrame containing the S&P 500 stocks. False if the request fails.
    :rtype: pd.DataFrame | Literal[False]
    """
    wikipedia_sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    resp = requests.get(wikipedia_sp500_url)

    if resp.status_code != 200:
        return False

    df = pd.DataFrame(columns=["Ticker", "Company", "Sector"])

    matches = re.finditer(
        r'<a\srel="nofollow"\sclass="external\stext"\shref=".*?">(\w+)<\/a>\s+<\/td>\s+<td>.*?>(.*?)<.*\s<td>(.*?)<',
        resp.text,
    )

    for match in matches:
        if match is None:
            continue
        df = df._append(
            {
                "Ticker": match.group(1),
                "Company": match.group(2),
                "Sector": match.group(3),
            },
            ignore_index=True,
        )

    return df


def organize_stocks(sp500_df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    This function creates a dictionary containing the S&P 500 stocks
    grouped by sector.

    :param sp500_df:
    :return: A dictionary containing the S&P 500 stocks grouped by sector.
    """
    sp500_dict = {}
    for sector in sp500_df["Sector"].unique():
        sp500_dict[sector] = []
    for ticker, sector in zip(sp500_df["Ticker"], sp500_df["Sector"]):
        sp500_dict[sector].append(ticker)
    if len(sp500_dict.keys()) != 11:
        print("Incorrect number of sectors")
        return {}
    return sp500_dict


def get_stock_returns(
    sector: str,
    ticker: str,
    start_date: str,
    end_date: str,
    data_dict: Dict[str, Dict[str, Dict[str, str]]],
    lock: Lock,
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
        df = Stooq.download(f"{ticker}.US", start_date, end_date)

        if len(df) == 0:
            print(f"Issue with stock: {ticker}")
            return

        initial_price = df["Close"].iloc[0]
        final_price = df["Close"].iloc[-1]
        total_return = (final_price - initial_price) / initial_price * 100

        print(f"{sector} - {ticker} - {total_return:.2f}")

        with lock:
            print(f"{ticker} - {total_return:.2f}")
            if total_return > data_dict[sector]["Best"]["Return"]:
                data_dict[sector]["Best"]["Ticker"] = ticker
                data_dict[sector]["Best"]["Return"] = total_return

            if total_return < data_dict[sector]["Worst"]["Return"]:
                data_dict[sector]["Worst"]["Ticker"] = ticker
                data_dict[sector]["Worst"]["Return"] = total_return
    except:
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
            "Best": {"Ticker": "", "Return": 0},
            "Worst": {"Ticker": "", "Return": 0},
        }

    start = datetime.strptime(start_date, "%Y%m%d")

    end = start + parse_timeframe(timeframe)

    for sector in tqdm(sp500_sectors.keys(), desc="Sector Loop", position=0):
        pool = ThreadPool(2)
        lock = Lock()
        for stock in tqdm(
            sp500_sectors[sector], desc="Stock Loop", position=1, leave=False
        ):
            pool.apply_async(
                get_stock_returns,
                (
                    sector,
                    stock,
                    start.strftime("%Y%m%d"),
                    end.strftime("%Y%m%d"),
                    data,
                    lock,
                ),
            )
        pool.close()
        pool.join()

    return data, end


if __name__ == "__main__":
    aapl_df = MacroTrends.download("AAPL", "2025-02-09", "2025-02-12")

    print(aapl_df.head())
    print(aapl_df.tail())


# if __name__ == "__main__":
#     sp500_df = sp500_sectors()
#
#     if sp500_df is False:
#         print("Failed to scrape S&P 500")
#         exit(1)
#
#     sp500_dict = organize_stocks(sp500_df)
#
#     print("Stocks Organized")
#
#     data, end = get_sector_pairs("20231012", "1y", sp500_dict)
#
#     print(json.dumps(data, indent=4))
#
#     print(end.strftime("%Y-%m-%d"))
