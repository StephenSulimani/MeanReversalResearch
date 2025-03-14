from datetime import datetime

from sector import Sector, sp500_sectors
from testbench import Portfolio
from helpers import *
import pandas as pd


if __name__ == "__main__":
    sectors = sp500_sectors()

    START_DATE = "2022-10-12"
    MIDPOINT_DATE = "2023-10-12"
    END_DATE = "2024-01-12"

    sector_list = []

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
    portfolio.run_strategy(sector_list)

    # graphing
    file_path = "data/SPY.csv"
    spy_df = import_and_filter_csv(file_path)
    spy_series = df_to_close_series(spy_df)

    port_df = pd.read_csv('TestPortfolio.csv', parse_dates=['Date'])
    test_port_df = port_df.copy()

    test_port_df.set_index('Date', inplace=True)
    port_series = test_port_df['0']

    pretty_line_chart(port_series, spy_series)

