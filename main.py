import json
import re
from datetime import datetime
from typing import Dict, List

import pandas as pd
import requests


def sp500_sectors() -> pd.DataFrame | bool:
    """
    This function scrapes the S&P 500 stocks from the Wikiepedia page,
    and creates a DataFrame containing each stock's ticker, company name,
    and GICS Sector.

    :return: A DataFrame containing the S&P 500 stocks. False if the request fails.
    :rtype: pd.DataFrame | bool
    """
    wikipedia_sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    resp = requests.get(wikipedia_sp500_url)

    if resp.status_code != 200:
        return False

    df = pd.DataFrame(columns=["Ticker", "Company", "Sector"])

    matches = re.finditer(
        r'<a\srel="nofollow"\sclass="external\stext"\shref=".*?">(\w+)<\/a>\s+<\/td>\s+<td>.*?>(.*?)<.*\s<td>(.*?)<',
        resp.text,
    )

    for match in matches:
        if match is None:
            continue
        df = df._append(
            {
                "Ticker": match.group(1),
                "Company": match.group(2),
                "Sector": match.group(3),
            },
            ignore_index=True,
        )

    return df


def organize_stocks(sp500_df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    This function creates a dictionary containing the S&P 500 stocks
    grouped by sector.

    :param sp500_df:
    :return: A dictionary containing the S&P 500 stocks grouped by sector.
    """
    sp500_dict = {}
    for sector in sp500_df["Sector"].unique():
        sp500_dict[sector] = []
    for ticker, sector in zip(sp500_df["Ticker"], sp500_df["Sector"]):
        sp500_dict[sector].append(ticker)
    if len(sp500_dict.keys()) != 11:
        print("Incorrect number of sectors")
        return {}
    return sp500_dict


def get_sector_pairs(
    start_date: str, timeframe: str, sp500_sectors: Dict[str, List[str]]
):
    """
    This function calculates the best performing stock and the worst performing stock
    for each sector in the S&P 500 over a given timeframe.

    :param start_date: Start date formatted YYYYMMDD.
    :param timeframe: Timeframe to look past start_date.
    :param sp500_sectors: Dictionary containing the S&P 500 stocks grouped by sector.
    """
    data = {}

    for key in sp500_sectors.keys():
        data[key] = {"Best": {}, "Worst": {}}

    start = datetime.strptime(start_date, "%Y%m%d")
