import random
import re
from io import StringIO
from typing import Dict, List, Tuple

import pandas as pd
import requests


class AlphaVantage:
    """
    API wrapper for AlphaVantage.co

    Attributes:
        api_keys: List[str]
    """

    def __init__(self, api_keys: List[str]):
        """
        Constructor for AlphaVantage

        Args:
            api_keys: List[str]
        """
        if not api_keys:
            self._load_text_keys()
        else:
            self.api_keys = api_keys
        self._session = requests.Session()

    def _load_text_keys(self):
        with open("api_keys.txt", "r") as f:
            self.api_keys = f.read().splitlines()

    def _save_keys(self):
        with open("api_keys.txt", "w") as f:
            f.write("\n".join(self.api_keys))

    @property
    def api_key(self) -> str:
        """
        Returns a random API key

        Returns:
            str
        """
        return random.choice(self.api_keys)

    @property
    def random_ip(self) -> str:
        """
        Returns a random IP address

        Returns:
            str
        """
        return ".".join(map(str, (random.randint(0, 255) for _ in range(4))))

    @property
    def random_email(self) -> str:
        """
        Returns a random email address

        Returns:
            str
        """
        return (
            "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(15))
            + "@gmail.com"
        )

    def gen_api_key(self) -> str:
        while True:
            try:
                response = requests.get(
                    "https://www.alphavantage.co/support/#api-key",
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Referer": "https://www.alphavantage.co/support/",
                        "X-Real-IP": self.random_ip,
                        "X-Forwarded-For": self.random_ip,
                    },
                )

                csrf_cookie = response.headers["Set-Cookie"]

                regex = r"csrftoken=(.*?);"

                csrf_token = re.search(regex, csrf_cookie).group(1)

                response = requests.post(
                    "https://www.alphavantage.co/create_post/",
                    f"first_text=deprecated&last_text=deprecated&occupation_text=Investor&organization_text=ranadgajkg&email_text={self.random_email}",
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Referer": "https://www.alphavantage.co/support/",
                        "X-Real-IP": self.random_ip,
                        "X-Forwarded-For": self.random_ip,
                        "Cookie": csrf_cookie,
                        "X-CSRFToken": csrf_token,
                    },
                )

                json_res = response.json()

                regex = r"key\sis:\s(.*?)\."

                key = re.search(regex, json_res["text"]).group(1)

                self.api_keys.append(key)

                self._save_keys()

                return key
            except:
                continue

    def call(self, endpoint: str) -> Tuple[requests.Response, str]:
        key = self.api_key
        return (
            self._session.get(
                f"https://www.alphavantage.co/query?function="
                + endpoint
                + "&apikey="
                + key,
                headers={
                    "X-Real-IP": self.random_ip,
                    "X-Forwarded-For": self.random_ip,
                },
            ),
            key,
        )

    def time_series(self, ticker: str) -> pd.DataFrame | None:
        while True:
            res = ""
            try:
                res, key = self.call(
                    f"TIME_SERIES_DAILY&outputsize=full&datatype=csv&symbol={ticker}"
                )

                res = res.text

                if "We have detected your" in res:
                    print("API Key Issue")
                    self.api_keys.remove(key)
                    self._save_keys()
                    continue

                if "Error Message" in res:
                    return None

                csv_file = StringIO(res)

                df = pd.read_csv(csv_file)

                # Rename timestamp column to date:
                df.rename(columns={"timestamp": "date"}, inplace=True)

                df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

                df.set_index("date", inplace=True)

                return df
            except:
                print(res)
                print(ticker)
