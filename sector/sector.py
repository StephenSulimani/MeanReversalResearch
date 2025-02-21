from datetime import datetime
from typing import List, Tuple

import pandas as pd

from financialcalc.positions import PositionType, calculate_position


class Sector:
    sector_name: str
    sector_stocks = []
    start_date: datetime
    midpoint_date: datetime
    end_date: datetime

    best_stock: str = ""
    best_stock_df: pd.DataFrame
    best_stock_performance: float

    worst_stock: str = ""
    worst_stock_df: pd.DataFrame
    worst_stock_performance: float

    def __init__(self, sector_name: str, sector_stocks: List[str]):
        """
        The constructor for the Session class.

        :param sector_name: The name of the sector.
        :param sector_stocks: The stock tickers contained within the sector.
        """
        # Define Sector Properties
        self.sector_name = sector_name
        self.sector_stocks = sector_stocks

    def set_dates(self, start_date: str, midpoint_date: str, end_date: str):
        """
        The function to set the start, midpoint, and end dates.

        :param start_date: The date to begin the analysis. %Y-%m-%d
        :param midpoint_date: The date to end the analysis and open the position. %Y-%m-%d
        :param end_date: The date to close the position. %Y-%m-%d
        """
        # Parse Datetime Strings
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.midpoint_date = datetime.strptime(midpoint_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")

    @staticmethod
    def load_stock(stock_ticker: str) -> pd.DataFrame:
        """
        Loads and returns a stock's dataframe.

        :param stock_ticker: The ticker of the stock.
        :return: The DataFrame representing the stock's historical price.
        :rtype: pd.DataFrame
        """
        # Change In Production!!
        df = pd.read_csv(f"data/{stock_ticker}.csv")
        df = df.set_index("Date")
        df.index = pd.to_datetime(df.index)
        return df

    def calculate_best_worst(self):
        """
        Calculates the best performing and worst performing
        stocks in the sector.
        """
        for ticker in self.sector_stocks:
            try:
                original_df = self.load_stock(ticker)

                df = original_df.loc[self.start_date : self.midpoint_date]
                initial_price = df["Open"].iloc[0]
                final_price = df["Close"].iloc[-1]

                performance = (final_price - initial_price) / initial_price * 100

                if self.best_stock == "" or performance > self.best_stock_performance:
                    self.best_stock = ticker
                    self.best_stock_df = original_df
                    self.best_stock_performance = performance

                if self.worst_stock == "" or performance < self.worst_stock_performance:
                    self.worst_stock = ticker
                    self.worst_stock_df = original_df
                    self.worst_stock_performance = performance
            except:
                # In case the ticker doesn't have sufficient data, it will
                # be automatically excluded.
                pass

    def test_best_worst(self) -> Tuple[float, float]:
        """
        Calculate the performance of the SHORT and LONG positions,
        for the best and worst stocks in a sector, respectively.

        :return: A tuple of the best stock's position performance and
        the worst stock's position performance.
        """
        best_df = self.best_stock_df.loc[self.midpoint_date : self.end_date]
        worst_df = self.worst_stock_df.loc[self.midpoint_date : self.end_date]

        tested_best_performance = calculate_position(best_df, PositionType.SHORT)
        tested_worst_performance = calculate_position(worst_df, PositionType.LONG)

        return tested_best_performance, tested_worst_performance

    def run_calculations(self, start_date: str, midpoint_date: str, end_date: str):
        """
        The master function for the Sector class that runs all
        calculations needed to determine the best and worst stocks
        in a sector, and then tests the mean reversion strategy by
        opening a SHORT and LONG position for the best and worst stocks,
        respectively. Finally, the returns are calculated for the two
        positions and printed to the console and graphed.

        :param start_date: The date to begin the analysis. %Y-%m-%d
        :param midpoint_date: The date to end the analysis and open the position. %Y-%m-%d
        :param end_date: The date to close the position. %Y-%m-%d
        """
        self.set_dates(start_date, midpoint_date, end_date)
        self.calculate_best_worst()
        print(f"{self.sector_name}: {self.best_stock} vs {self.worst_stock}")
        self.test_best_worst()
