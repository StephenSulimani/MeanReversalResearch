import sys
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd

from helpers import *
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
    portfolio.run_strategy(sector_list, random_stocks=True)

    # portfolio = pd.read_csv("TestPortfolio.csv")
    # portfolio["Date"] = pd.to_datetime(portfolio["Date"], format="%Y-%m-%d")
    # portfolio.set_index("Date", inplace=True)

    # spy = pd.read_csv("data/SPY.csv")
    # spy["Date"] = pd.to_datetime(spy["Date"], format="%Y-%m-%d")
    # spy.set_index("Date", inplace=True)
    # spy = spy.loc[portfolio.index]

    # # Normalize Starting Close value of spy to 1000000, where the first close value is 1000000, and the following values are scaled
    # spy["Close"] = spy["Close"] * 1000000 / spy["Close"].iloc[0]

    # print(portfolio.head())

    # # Plot spy["Close"] and portfolio on same graph
    # plt.plot(spy["Close"], label="SPY")
    # plt.plot(portfolio, label="Portfolio")
    # plt.legend()
    # plt.show()
