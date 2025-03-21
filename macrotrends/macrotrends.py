from datetime import datetime

import pandas as pd
import requests


class MacroTrends:
    def __init__(self):
        pass

    @staticmethod
    def download(
        ticker: str, start_date="00-00-00", end_date="00-00-00"
    ) -> pd.DataFrame:
        """
        Downloads stock data for a given ticker from MacroTrends.

        Args:
            start_date (str): The start date of the data to download, formatted as YYYY-MM-DD.
                Defaults to the stock's inception.
            end_date (str): The end date of the data to download, formatted as YYYY-MM-DD.
                Defaults to the most recent available date.
            ticker (str): The stock ticker to download data for.

        Returns:
            Any: Description of the returned value.
        """

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Referer": f"https://www.macrotrends.net/assets/php/stock_price_history.php?t={ticker}",
        }

        resp = requests.get(
            f"https://www.macrotrends.net/assets/php/stock_data_download.php?t={ticker}",
            headers=headers,
        )

        if resp.status_code != 200:
            raise Exception("Failed to download stock data")
            resp.raise_for_status()

        lines = resp.text.split("\n")

        cleaned_lines = lines[15:]

        df = pd.DataFrame(
            [line.split(",") for line in cleaned_lines],
            columns=["Date", "Open", "High", "Low", "Close", "Volume"],
        )
        df = df.set_index("Date")

        df.index = pd.to_datetime(df.index, format="%Y-%m-%d")

        df = df.dropna(how="any")

        if start_date != "00-00-00":
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            df = df[df.index >= start_date]

        if end_date != "00-00-00":
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            df = df[df.index <= end_date]

        return df
