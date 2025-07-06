"""
The purpose of StockPicker.py is to take a CSV structured as follows:

Date, <perm_no_1>, <perm_no_2>, ..., <perm_no_n>
01-01-2000, <cluster_number>, <cluster_number>, ..., <cluster_number>

Additionally, StockPicker.py takes an argument for n, where n is the number of
stocks to pick for a each kind of position.

To put it simply, n*2 is the total number of stocks picked for each cluster.

The output of StockPicker.py will be two DataFrames, one for the best performing stocks,
and one for the worst performing stocks. It will use the date range as defined in the
cluster csv.

Authors:
Venn Reddy, University of Georgia
Stephen Sulimani, University of Georgia

2025
"""

import json
import os
import sys
from multiprocessing.pool import ThreadPool
from threading import Lock
from typing import Dict, List, Tuple, cast

import pandas as pd
from tqdm import tqdm

from AlphaVantage import AlphaVantage


def load_stock_df(ticker: str) -> pd.DataFrame | None:
    """
    Loads a stock's historical daily price data, uses
    an existing CSV if it exists, otherwise it pulls it
    from AlphaVantage.

    Args:
        ticker: The ticker of the stock to load.

    Returns:
        The DataFrame representing the stock's historical prices.
    """
    if os.path.exists("data/" + ticker + ".csv"):
        df = pd.read_csv("data/" + ticker + ".csv")
        df = cast(pd.DataFrame, df)
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
        df.set_index("date", inplace=True)
        return df
    return None
    df = AlphaVantage([]).time_series(ticker)
    if df is None:
        return None
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/" + ticker + ".csv")
    return df


def calculate_return(stock_df: pd.DataFrame, start_date: str, end_date: str) -> float:
    """
    Calculate the return between start_date and end_date.

    Args:
        stock_df: The DataFrame representing the stock's historical prices.
        start_date: The start date of the return.
        end_date: The end date of the return.

    Returns:
        The return between start_date and end_date.

    """
    try:
        end_movement = 0
        start_movement = 0
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        while end_dt not in stock_df.index:
            end_dt -= pd.Timedelta(days=1)
            end_movement += 1
        while start_dt not in stock_df.index:
            start_dt += pd.Timedelta(days=1)
            start_movement += 1

        if end_movement > 7 or start_movement > 7:
            return None

        start_price = stock_df.loc[start_dt]["close"]
        end_price = stock_df.loc[end_dt]["close"]
        return (end_price - start_price) / start_price
    except:
        # If an exception is thrown, that means the date range is invalid for this specific stock.
        return None


def get_date_range(cluster_csv: str) -> Tuple[List[str], List[str]]:
    """
    Reads through the cluster csv and returns the start and end dates.

    Args:
        cluster_csv: The cluster csv filepath.

    Returns:
        A tuple of the start and end dates.
    """
    df = pd.read_csv(cluster_csv)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
    start_date = df["Date"].min()
    end_date = df["Date"].max()

    # Get an array of all of the months included in the range
    first_months = []
    last_months = []
    first_days = []
    last_days = []

    all_dates = pd.date_range(start=start_date, end=end_date)

    for i, date in enumerate(all_dates):
        month = date.strftime("%Y-%m")
        if month not in first_months:
            first_months.append(month)
            first_days.append(date.strftime("%Y-%m-%d"))
        if i == len(all_dates) - 1:
            last_months.append(month)
            last_days.append(date.strftime("%Y-%m-%d"))
            continue

        next_day_month = all_dates[i + 1].strftime("%Y-%m")
        if month != next_day_month:
            last_months.append(month)
            last_days.append(date.strftime("%Y-%m-%d"))

    return first_days, last_days


def get_sectors(cluster_csv: str) -> Dict:
    """
    Reads through the cluster csv and returns a dictionary of sectors and stocks.

    Args:
        cluster_csv: The cluster csv filepath.

    Returns:
        A dictionary of sectors and stocks.
    """
    df = pd.read_csv(cluster_csv)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
    end_date = df["Date"].max()
    df.set_index("Date", inplace=True)

    sectors = {}

    for column in df.columns:
        try:
            sector = int(df.loc[end_date][column])

            if sector not in sectors:
                sectors[sector] = []

            sectors[sector].append(column)
        except:
            pass

    return sectors


type Boundary = Tuple[pd.DatetimeIndex, pd.DatetimeIndex]
type BoundaryList = List[Boundary]


def best_worst(
    tickers: List[str], n: int, date_range: pd.DatetimeIndex
) -> Tuple[List[str], List[str]]:
    """
    Returns the best and worst performing stocks.

    Args:
        tickers: The stock's to compare.
        n: The number of "best" stocks and the number of "worst" stocks.

    Returns:
        The best and worst performing stocks.
    """
    performance = {}

    for ticker in tickers:
        stock_df = load_stock_df(ticker)
        if stock_df is not None:
            performance[ticker] = calculate_return(
                stock_df, date_range[0].date(), date_range[-1].date()
            )

    performance = {k: v for k, v in performance.items() if v is not None}

    best = sorted(performance, key=performance.get, reverse=True)[:n]
    worst = sorted(performance, key=performance.get)[:n]

    return best, worst


def define_boundaries(
    first_days: List[str], last_days: List[str], lookback_months: int
) -> BoundaryList:
    boundaries = []
    i = lookback_months

    while i < len(first_days):
        boundaries.append(
            (
                pd.date_range(
                    start=pd.to_datetime(first_days[i - lookback_months]),
                    end=pd.to_datetime(last_days[i - 1]),
                ),
                pd.date_range(
                    start=pd.to_datetime(first_days[i]),
                    end=pd.to_datetime(last_days[i]),
                ),
            )
        )
        i += 1

    return boundaries


# if __name__ == "__main__":
#     tickers = ["MSFT", "AMZN", "KO", "MA", "COST", "LUV", "XOM", "TSLA"]
#
#     df = pd.DataFrame({"Date": pd.date_range("1990-01-01", "2025-04-17")})
#
#     df.set_index("Date", inplace=True)
#
#     for ticker in tickers:
#         stock_df = load_stock_df(ticker)
#         df[ticker] = load_stock_df(ticker)["close"]
#
#     df = df.dropna()
#     df.to_csv("venn.csv")


def crunch_data(
    boundary: Boundary, n: int, sectors: Dict, lock: Lock, pbar: tqdm
) -> Dict:
    lookback, test = boundary

    best = []
    worst = []

    lock2 = Lock()

    # pool = ThreadPool(5)

    def crunch_sector(tickers: List[str]):
        best_stocks, worst_stocks = best_worst(tickers, n, lookback)
        with lock:
            pbar.update(1)

        return (best_stocks, worst_stocks)
        with lock2:
            best.extend(best_stocks)
            worst.extend(worst_stocks)

    # processed = pool.map_async(crunch_sector, list(sectors.values()))

    # pool.close()
    # pool.join()

    # for best_stocks, worst_stocks in processed.get():
    #     best.extend(best_stocks)
    #     worst.extend(worst_stocks)

    for _, tickers in sectors.items():
        best_stocks, worst_stocks = crunch_sector(tickers)
        best.extend(best_stocks)
        worst.extend(worst_stocks)

    return {
        "lookback": {
            "start": lookback[0].date().strftime("%Y-%m-%d"),
            "end": lookback[-1].date().strftime("%Y-%m-%d"),
        },
        "test": {
            "start": test[0].date().strftime("%Y-%m-%d"),
            "end": test[-1].date().strftime("%Y-%m-%d"),
        },
        "best_stocks": best,
        "worst_stocks": worst,
    }

    for _, tickers in sectors.items():
        pool.apply_async(crunch_sector, args=(tickers,))
        continue
        with lock:
            pbar.update(1)
            print("sector done")
        best_stocks, worst_stocks = best_worst(tickers, n, lookback)
        best.extend(best_stocks)
        worst.extend(worst_stocks)
    pool.close()
    pool.join()

    return {
        "lookback": {
            "start": lookback[0].date().strftime("%Y-%m-%d"),
            "end": lookback[-1].date().strftime("%Y-%m-%d"),
        },
        "test": {
            "start": test[0].date().strftime("%Y-%m-%d"),
            "end": test[-1].date().strftime("%Y-%m-%d"),
        },
        "best_stocks": best,
        "worst_stocks": worst,
    }


if __name__ == "__main__":
    # stonk = load_stock_df("AAPL")
    # print(stonk.head())
    # stonk_return = calculate_return(stonk, "2022-01-01", "2023-01-01")
    # print(stonk_return)
    if len(sys.argv) != 5:
        print("Usage: python StockPicker.py <cluster_csv> <n> <lookback_months> <output_json>")
        sys.exit(1)

    cluster_csv = sys.argv[1]
    n = int(sys.argv[2])
    lookback_months = int(sys.argv[3])
    output_filename = sys.argv[4]

    if not output_filename.endswith(".json"):
        output_filename += ".json"

    first_days, last_days = get_date_range(cluster_csv)

    boundaries = define_boundaries(first_days, last_days, lookback_months)

    sectors = get_sectors(cluster_csv)

    pool = ThreadPool(50)

    pbar = tqdm(total=len(boundaries) * len(sectors))

    lock = Lock()

    processed_data = pool.map_async(
        lambda boundary: crunch_data(boundary, n, sectors, lock, pbar), boundaries
    )

    pool.close()
    pool.join()
    pbar.close()

    complete_data = processed_data.get()

    # Sort complete_data by lookback["start"]
    complete_data = sorted(complete_data, key=lambda x: x["lookback"]["start"])

    with open(output_filename, "w") as f:
        json.dump(complete_data, f, indent=4)

    sys.exit(1)

    sectors = get_sectors(cluster_csv)

    best_stocks = []
    worst_stocks = []

    for sector, tickers in sectors.items():
        best, worst = best_worst(tickers, n)
        best_stocks.extend(best)
        worst_stocks.extend(worst)
        print(f"Best stocks in sector {sector}: {best}")
        print(f"Worst stocks in sector {sector}: {worst}")

    df = pd.DataFrame({"Date": pd.date_range(start_date, end_date)})

    df.set_index("Date", inplace=True)

    for ticker in best_stocks:
        stock_df = load_stock_df(ticker)
        df[ticker] = stock_df["close"]

    df = df.dropna()

    df.to_csv("Best.csv")

    df = pd.DataFrame({"Date": pd.date_range(start_date, end_date)})

    df.set_index("Date", inplace=True)

    for ticker in worst_stocks:
        stock_df = load_stock_df(ticker)
        df[ticker] = stock_df["close"]

    df = df.dropna()

    df.to_csv("Worst.csv")

    #     df = pd.DataFrame({"Date": pd.date_range("1990-01-01", "2025-04-17")})
#
#     df.set_index("Date", inplace=True)
#
#     for ticker in tickers:
#         stock_df = load_stock_df(ticker)
#         df[ticker] = load_stock_df(ticker)["close"]
#
#     df = df.dropna()
#     df.to_csv("venn.csv")
