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
        # Define Sector Properties
        self.sector_name = sector_name
        self.sector_stocks = sector_stocks

    def set_dates(self, start_date: str, midpoint_date: str, end_date: str):
        # Parse Datetime Strings
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.midpoint_date = datetime.strptime(midpoint_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")

    @staticmethod
    def load_stock(stock_ticker: str):
        # Change In Production!!
        df = pd.read_csv(f"data/{stock_ticker}.csv")
        df = df.set_index("Date")
        df.index = pd.to_datetime(df.index)
        return df

    def calculate_best_worst(self):
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

        :return: Tuple[float, float]
        """
        best_df = self.best_stock_df.loc[self.midpoint_date : self.end_date]
        worst_df = self.worst_stock_df.loc[self.midpoint_date : self.end_date]

        tested_best_performance = calculate_position(best_df, PositionType.SHORT)
        tested_worst_performance = calculate_position(worst_df, PositionType.LONG)

        return tested_best_performance, tested_worst_performance

    def run_calculations(self, start_date: str, midpoint_date: str, end_date: str):
        self.set_dates(start_date, midpoint_date, end_date)
        self.calculate_best_worst()
        print(f"{self.sector_name}: {self.best_stock} vs {self.worst_stock}")
        self.test_best_worst()
