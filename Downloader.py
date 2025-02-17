import os
import time

from tqdm import tqdm

from macrotrends import MacroTrends
from sp500 import organize_stocks, sp500_sectors


def main():
    sp500_df = sp500_sectors()

    if sp500_df is False:
        print("Failed to scrape S&P 500")
        exit(1)

    sp500_dict = organize_stocks(sp500_df)

    # Create "data" directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")

    for sector in tqdm(sp500_dict.keys(), desc="Sector", position=0):
        for ticker in tqdm(sp500_dict[sector], desc="Stock", position=1, leave=False):
            if os.path.exists(f"data/{ticker}.csv"):
                continue
            while True:
                try:
                    df = MacroTrends.download(ticker)
                    df.to_csv(f"data/{ticker}.csv")
                    time.sleep(25)
                    break
                except:
                    pass


if __name__ == "__main__":
    main()
