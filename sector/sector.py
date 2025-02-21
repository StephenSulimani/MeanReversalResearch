import os
from datetime import datetime
from typing import List, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from financialcalc.positions import PositionType, calculate_position


class Sector:
    sector_name: str
    sector_stocks: List[str] = []
    start_date: datetime
    midpoint_date: datetime
    end_date: datetime

    best_stock: str = ""
    best_stock_df: pd.DataFrame
    best_stock_performance: float

    worst_stock: str = ""
    worst_stock_df: pd.DataFrame
    worst_stock_performance: float

    short_performance: float
    long_performance: float

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

    def test_best_worst(self):
        """
        Calculate the performance of the SHORT and LONG positions,
        for the best and worst stocks in a sector, respectively.
        """
        best_df = self.best_stock_df.loc[self.midpoint_date : self.end_date]
        worst_df = self.worst_stock_df.loc[self.midpoint_date : self.end_date]

        self.short_performance = calculate_position(best_df, PositionType.SHORT)
        self.long_performance = calculate_position(worst_df, PositionType.LONG)

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

    def graph_sectors(self):
        """
        Graphs the best and worst stocks in a sector between given date ranges, with the short of the best
        stock and long of the worst stock shown after the midpoint.
        """
        best_df = self.best_stock_df.loc[self.start_date : self.end_date].copy()
        worst_df = self.worst_stock_df.loc[self.start_date : self.end_date].copy()

        # Plotting the cumulative return of the best performing stock in the sector
        initial_close = best_df["Close"].iloc[0]
        best_df["Cum_Return"] = (
            (best_df["Close"] - initial_close) / initial_close
        ) * 100

        best_df_first = best_df.loc[: self.midpoint_date]
        best_df_second = best_df.loc[self.midpoint_date :]

        plt.plot(
            best_df_first.index,
            best_df_first["Cum_Return"],
            label=f"{self.best_stock} (Best)",
            color="blue",
        )
        plt.plot(
            best_df_second.index,
            best_df_second["Cum_Return"],
            linestyle="dashed",
            color="blue",
            label=f"{self.best_stock} (Backtesting) | Position Return: {self.short_performance:.2f}%",
        )

        # Plotting the cumulative return of the worst performing stock in the sector
        initial_close = worst_df["Close"].iloc[0]
        worst_df["Cum_Return"] = (
            (worst_df["Close"] - initial_close) / initial_close
        ) * 100

        worst_df_first = worst_df.loc[: self.midpoint_date]
        worst_df_second = worst_df.loc[self.midpoint_date :]

        plt.plot(
            worst_df_first.index,
            worst_df_first["Cum_Return"],
            label=f"{self.worst_stock} (Worst)",
            color="red",
        )
        plt.plot(
            worst_df_second.index,
            worst_df_second["Cum_Return"],
            linestyle="dashed",
            color="red",
            label=f"{self.worst_stock} (Backtesting) | Position Return: {self.long_performance:.2f}%",
        )

        # Collecting absolute values of all the max & min returns to find the largest in either direction
        best_max, best_min = (best_df["Cum_Return"].max(), best_df["Cum_Return"].min())
        worst_max, worst_min = (
            worst_df["Cum_Return"].max(),
            worst_df["Cum_Return"].min(),
        )
        all_extrema = [abs(best_max), abs(best_min), abs(worst_max), abs(worst_min)]

        # Setting the y-limit to the highest extrema + a 10% buffer:
        y_lim = max(all_extrema)
        buffer = 0.1 * y_lim
        plt.ylim(-y_lim - buffer, y_lim + buffer)

        # Drawing vertical dashed line at midpoint
        plt.axvline(
            mdates.date2num(self.midpoint_date),
            color="black",
            linestyle="dashed",
            linewidth=2,
            label="Start of Backtest",
        )

        # Labeling and setting up my plot
        plt.title(f"{self.sector_name}: Best and Worst Stocks Compared")
        plt.xlabel("Date")
        plt.ylabel("Stock Return (%)")
        plt.legend()
        plt.grid(True)

        # Saving the plot onto local storage (I .gitignored ./graphs but we can test non-local storage in future)
        image_directory = "./graphs"
        os.makedirs(image_directory, exist_ok=True)
        image_path = f"{image_directory}/{self.sector_name}.png"
        plt.savefig(image_path)
        plt.close()

        print(
            f"Graphed and saved stock comparison of {self.best_stock} vs {self.worst_stock}. in {image_path}"
        )
