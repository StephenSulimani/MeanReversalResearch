import sys
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd

from helpers import (df_to_close_series, import_and_filter_csv,
                     pretty_line_chart)
from sector import Sector, sp500_sectors
from testbench import Portfolio

if __name__ == "__main__":
    sectors = sp500_sectors()

    START_DATE = "2022-10-12"
    MIDPOINT_DATE = "2023-10-12"
    END_DATE = "2024-01-12"

    sector_list = []

    if sectors is None or sectors is False:
        print("No Sectors Found")
        sys.exit(1)

    for sector_name, sector_stocks in sectors.items():
        sector = Sector(sector_name, sector_stocks)

        #        sector.run_calculations(START_DATE, MIDPOINT_DATE, END_DATE)
        #        sector.graph_sectors()

        sector_list.append(sector)
    start_date = "2020-01-01"
    end_date = "2024-01-01"

    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

    portfolio = Portfolio(1000000, start_date_dt, "3m", "1m", end_date_dt)

    # portfolio.run_strategy(sector_list)

    # # Graphing
    # SPY
    file_path = "data/SPY.csv"
    spy_df = import_and_filter_csv(file_path)
    spy_series = df_to_close_series(spy_df)

    # # Mean Reversal Portfolio
    port_df = pd.read_csv("TestPortfolio.csv", parse_dates=["Date"])
    test_port_df = port_df.copy()
    test_port_df.set_index("Date", inplace=True)
    port_series = test_port_df["0"]

    # # Random Test One
    rand_one_df = pd.read_csv("RandomTest1.csv", parse_dates=["Date"])
    test_rand_one_df = rand_one_df.copy()
    test_rand_one_df.set_index("Date", inplace=True)
    rand_one_series = test_rand_one_df["0"]

    # # Random Test Two
    rand_two_df = pd.read_csv("RandomTest2.csv", parse_dates=["Date"])
    test_rand_two_df = rand_two_df.copy()
    test_rand_two_df.set_index("Date", inplace=True)
    rand_two_series = test_rand_two_df["0"]

    # # Random Test Two
    rand_three_df = pd.read_csv("RandomTest3.csv", parse_dates=["Date"])
    test_rand_three_df = rand_three_df.copy()
    test_rand_three_df.set_index("Date", inplace=True)
    rand_three_series = test_rand_three_df["0"]

    # # Plot of Mean Reversal Portfolio vs SPY
    pretty_line_chart(port_series, spy_series)

    # # Plot of Mean Reversal Portfolio vs SPY vs Random Tests
    pretty_line_chart(
        port_series, spy_series, rand_one_series, rand_two_series, rand_three_series
    )
