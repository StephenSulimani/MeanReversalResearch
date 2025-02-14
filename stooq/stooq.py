import re
import time
from typing import List

import pandas as pd
import requests


class Stooq:
    def __init__(self):
        pass

    @staticmethod
    def queryTicker(ticker: str) -> List[object]:
        """Queries Stooq for tickers that are related
        to the given ticker. Returns available tickers to the user.

        Args:
            ticker (str): Ticker to search for

        Returns:
            List[object]: List of objects for each found ticker,
            including full ticker name, full company name, exchange,
            price, and daily increase.
        """

        current_epoch = int(time.time())

        request_url = f"https://stooq.com/cmp/?{current_epoch}&q={ticker}"

        response = requests.get(request_url)

        res_body = response.text

        res_body = res_body.replace("window.cmp_r('", "")
        res_body = res_body.replace("');", "")
        res_body = res_body.replace("<b>", "")
        res_body = res_body.replace("</b>", "")

        options = res_body.split("|")

        stocks = []

        for option in options:
            option = option.strip()
            match = re.search(r"(.*?)\~(.*?)\~(.*?)\~(.*?)\~(.*?)\~", option)

            if not isinstance(match, re.Match):
                continue

            if any(match[i] == "" for i in range(1, 6)):
                continue
            stocks.append(
                {
                    "Ticker": match[1],
                    "Name": match[2],
                    "Exchange": match[3],
                    "Price": float(match[4]),
                    "Daily_Increase": float(match[5].replace("%", "")),
                }
            )

        return stocks

    @staticmethod
    def download(ticker: str, startDate: str, endDate: str) -> pd.DataFrame:
        """Downloads historical data for a given ticker during a
        given period of time. Returns a pandas DataFrame representing
        the data.

        Args:
            ticker (str): Exact ticker to pull historical data for.
            startDate (str): Date for historical data to begin, example:
            20231012 -> October 12, 2023.
            endDate (str): Date for historical data to end. Same format as startDate.

        Returns:
            pandas.DataFrame: DataFrame representing the stock's historical data.
            Includes columns for date, open, close, high, low, and volume.
        """
        request_url = (
            f"https://stooq.com/q/d/l/?s={ticker}&d1={startDate}&d2={endDate}&i=d"
        )

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = requests.get(request_url, headers=headers)

        df = pd.DataFrame(
            columns=pd.Index(["Date", "Open", "High", "Low", "Close", "Volume"])
        )

        res_body = response.text

        rows = res_body.split("\n")

        rows = rows[1:]

        data = {
            "Date": [],
            "Open": [],
            "High": [],
            "Low": [],
            "Close": [],
            "Volume": [],
        }

        for row in rows:
            params = row.split(",")

            if len(params) < 6:
                continue

            data["Date"].append(params[0].strip())
            data["Open"].append(float(params[1].strip()))
            data["High"].append(float(params[2].strip()))
            data["Low"].append(float(params[3].strip()))
            data["Close"].append(float(params[4].strip()))
            data["Volume"].append(int(float(params[5].strip())))

        df = pd.DataFrame(data)

        df = df.set_index("Date")

        df.index = pd.to_datetime(df.index, format="%Y-%m-%d")

        if len(df) == 0 and ".US" not in ticker.upper():
            return Stooq.download(f"{ticker}.US", startDate, endDate)

        return df
