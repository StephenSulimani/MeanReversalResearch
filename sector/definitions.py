import re
from typing import Dict, List, Literal

import requests


def sp500_sectors() -> Dict[str, List[str]] | Literal[False]:
    """
    This function scrapes the S&P 500 stocks from the Wikipedia page,
    and creates a Dict mapping each sector to a list of stock tickers.

    :return: A Dict organizing all of the S&P 500 stocks. False if the request fails.
    :rtype: pd.DataFrame | Literal[False]
    """
    wikipedia_sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    resp = requests.get(wikipedia_sp500_url)

    if resp.status_code != 200:
        return False

    matches = re.finditer(
        r'<a\srel="nofollow"\sclass="external\stext"\shref=".*?">(\w+)<\/a>\s+<\/td>\s+<td>.*?>(.*?)<.*\s<td>(.*?)<',
        resp.text,
    )

    sector_dict: Dict[str, List[str]] = {}

    for match in matches:
        if match is None:
            continue
        if match.group(3) in sector_dict:
            sector_dict[match.group(3)].append(match.group(1))
        else:
            sector_dict[match.group(3)] = [match.group(1)]

    return sector_dict
