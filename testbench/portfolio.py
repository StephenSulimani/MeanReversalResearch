import random
from datetime import datetime
from typing import List

import pandas as pd

from financialcalc.positions import PositionType, calculate_position_daily
from helpers import get_row_by_date, parse_timeframe
from sector.sector import Sector


class Portfolio:
    balance = 0
    start_date: datetime
    backtest_interval: str
    test_interval: str
    end_date: datetime

    def __init__(
        self,
        starting_balance: float,
        start_date: datetime,
        backtest_interval: str,
        test_interval: str,
        end_date: datetime,
    ):
        """
        Constructor for the Portfolio class.

        :param starting_balance: The balance to start the portfolio with.
        :param start_date: The date to begin the portfolio at.
        :param backtest_interval: The interval to lookback to determine best and worst performing stocks (1m for 1 month, 1d for 1 day, etc.)
        :param test_interval: The interval to have the position open for.
        :param end_date: The date to end the portfolio at.
        """

        self.balance = starting_balance
        self.start_date = start_date
        self.backtest_interval = backtest_interval
        self.test_interval = test_interval
        self.end_date = end_date

    def calculate_positions(
        self,
        capital: float,
        best_stock: str,
        worst_stock: str,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.Series:
        best_stock_df = Sector.load_stock(best_stock)
        worst_stock_df = Sector.load_stock(worst_stock)

        best_stock_df = best_stock_df.loc[start_date:end_date]
        worst_stock_df = worst_stock_df.loc[start_date:end_date]

        best_position = calculate_position_daily(
            capital / 2, best_stock_df, PositionType.SHORT
        )
        worst_position = calculate_position_daily(
            capital / 2, worst_stock_df, PositionType.LONG
        )

        return best_position + worst_position

    def run_strategy(self, sectors: List[Sector], random_stocks=False) -> pd.Series:
        backtest_timeframe_delta = parse_timeframe(self.backtest_interval)
        test_timeframe_delta = parse_timeframe(self.test_interval)

        utcnow = datetime.now()
        time_delta = utcnow + test_timeframe_delta - utcnow

        total_tests = (self.end_date - self.start_date) // time_delta

        print(f"Total Tests: {total_tests}")

        current_date = self.start_date

        portfolio_value = pd.Series()

        for i in range(total_tests):

            backtest_start_date = current_date - backtest_timeframe_delta
            backtest_end_date = current_date
            test_start_date = current_date
            test_end_date = current_date + test_timeframe_delta
            current_date = test_end_date

            sector_performance_series = pd.Series()

            for sector in sectors:
                sector.set_dates(
                    backtest_start_date.strftime("%Y-%m-%d"),
                    backtest_end_date.strftime("%Y-%m-%d"),
                    test_end_date.strftime("%Y-%m-%d"),
                )
                best_stock = ""
                worst_stock = ""

                while True:

                    if not random_stocks:
                        sector.calculate_best_worst()

                        best_stock = sector.best_stock
                        worst_stock = sector.worst_stock
                    else:
                        best_stock = random.choice(sector.sector_stocks)
                        worst_stock = random.choice(sector.sector_stocks)

                    capital = self.balance / len(sectors)
                    try:
                        positions = self.calculate_positions(
                            capital,
                            best_stock,
                            worst_stock,
                            test_start_date,
                            test_end_date,
                        )

                        if sector_performance_series.empty:
                            sector_performance_series = positions
                        else:
                            sector_performance_series += positions
                        break
                    except:
                        pass

            if portfolio_value.empty:
                portfolio_value = sector_performance_series
            else:
                portfolio_value = pd.concat(
                    [portfolio_value, sector_performance_series]
                )
            self.balance = float(portfolio_value.iloc[-1])

            print(f"Balance After Test {i+1}: {self.balance}")
            print(portfolio_value.tail(25))
            portfolio_value.to_csv("port.csv")

        return portfolio_value

    def run_custom_sectors(
        self, sector_definitions: pd.DataFrame, random_stocks=False
    ) -> pd.Series:
        backtest_timeframe_delta = parse_timeframe(self.backtest_interval)
        test_timeframe_delta = parse_timeframe(self.test_interval)

        utcnow = datetime.now()
        time_delta = utcnow + test_timeframe_delta - utcnow

        total_tests = (self.end_date - self.start_date) // time_delta

        print(f"Total Tests: {total_tests}")

        current_date = self.start_date

        portfolio_value = pd.Series()

        for i in range(total_tests):

            backtest_start_date = current_date - backtest_timeframe_delta
            backtest_end_date = current_date
            test_start_date = current_date
            test_end_date = current_date + test_timeframe_delta
            current_date = test_end_date

            sector_obj = {}

            # sector_definition = sector_definitions.loc[backtest_start_date]

            sector_definition = get_row_by_date(sector_definitions, backtest_start_date)

            # for each column in the row
            for column in sector_definition.index:
                value = sector_definition[column]
                if value not in sector_obj:
                    sector_obj[value] = []

                sector_obj[value].append(column)

            sectors = [Sector(name, sector_obj[name]) for name in sector_obj.keys()]

            sector_performance_series = pd.Series()

            for sector in sectors:
                sector.set_dates(
                    backtest_start_date.strftime("%Y-%m-%d"),
                    backtest_end_date.strftime("%Y-%m-%d"),
                    test_end_date.strftime("%Y-%m-%d"),
                )
                best_stock = ""
                worst_stock = ""

                while True:

                    if not random_stocks:
                        sector.calculate_best_worst()

                        best_stock = sector.best_stock
                        worst_stock = sector.worst_stock
                    else:
                        best_stock = random.choice(sector.sector_stocks)
                        worst_stock = random.choice(sector.sector_stocks)

                    capital = self.balance / len(sectors)
                    try:
                        positions = self.calculate_positions(
                            capital,
                            best_stock,
                            worst_stock,
                            test_start_date,
                            test_end_date,
                        )

                        if sector_performance_series.empty:
                            sector_performance_series = positions
                        else:
                            sector_performance_series += positions
                        break
                    except:
                        pass

            if portfolio_value.empty:
                portfolio_value = sector_performance_series
            else:
                portfolio_value = pd.concat(
                    [portfolio_value, sector_performance_series]
                )
            self.balance = float(portfolio_value.iloc[-1])

            print(f"Balance After Test {i+1}: {self.balance}")
            print(portfolio_value.tail(25))
            portfolio_value.to_csv("port2.csv")
