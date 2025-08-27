import json
import os
import sys
from multiprocessing.pool import ThreadPool
from threading import Lock
from typing import Dict, List, Tuple, cast
import matplotlib.pyplot as plt
import numpy as np
import datetime


import pandas as pd
from tqdm import tqdm

# from AlphaVantage import AlphaVantage


# ——— Style constants ———
GREY91 = "#e8e8e8"
GREY98 = "#fafafa"
PALETTE = ["#7F3C8D", "#11A579", "#3969AC", "#F2B701", "#E73F74", "#401BB8", "#000000"]  # up to 6 series



def get_values(filename: str):
    """
    Read a CSV file with 'end_date' and 'current_balance' columns,
    parse dates, and return a DataFrame.
    """

    print("Graphing results for " + filename + "...")
    df = pd.read_csv(filename, parse_dates=["end_date"])
    return df[["end_date", "current_balance"]].copy()

def graph_spy(filename: str):
    df = pd.read_csv(filename, parse_dates=["Date"])
    df = df.set_index("Date")
    df = df.loc["2020-03-31":"2023-12-31"]
    df["Returns"] = df["Adj Close"].pct_change()
    df = df.dropna()

if __name__ == "__main__":
    # Usage
    if len(sys.argv) <= 1:
        print("Insufficient arguments provided. Graphs tabular output files from Backtester.py")
        print("Usage: python StockPicker.py <output_file_1.csv> <output_file_2.csv> ... <output_file_n.csv>")
        sys.exit(1)

    print(f"Script name: {sys.argv[0]}")
    if len(sys.argv) > 1:
        print("Arguments passed:")
        for i, arg in enumerate(sys.argv[1:]):
            print(f"  Argument {i+1}: {arg}")
    else:
        print("No arguments provided.")

    pd.set_option('display.float_format', '{:.2f}'.format)

    # fig, ax = plt.subplots(figsize=(14, 8.5), dpi=100)
    fig, ax = plt.subplots(figsize=(14, 8.5))

    fig.patch.set_facecolor(GREY91)
    ax.set_facecolor(GREY98)

    for i in range(1, len(sys.argv)):
        filename = sys.argv[i]
        if not os.path.exists(filename):
            print(f"File {filename} does not exist. Skipping...")
            continue
        if not filename.endswith(".csv"):
            print(f"File {filename} is not a CSV file. Skipping...")
            continue
        data = get_values(filename)
        ax.plot(data['end_date'], data['current_balance'], label=filename, color=PALETTE[i % len(PALETTE)])

    # data = get_values('./output_n1.csv')
    # ax.plot(data['end_date'], data['current_balance'], label='output_n1.csv', color=PALETTE[0])
    ax.set(xlabel='Time', ylabel='Portfolio Value',
       title='Hierarchical vs Kmeans vs Random Portfolio Value Over Time')
    # ax.grid()
    # ax.legend(loc='upper left', fontsize='small')
    ax.legend(loc='upper left', fontsize='large')
    plt.xticks(rotation=45)
    plt.tight_layout()

    for year in range(2001, 2025):
        ax.axvline(datetime.datetime(year, 1, 1), color=GREY91, lw=2, zorder=0)


    plt.show()

    # for filename in sys.argv[1:]:
    #     if not os.path.exists(filename):
    #         print(f"File {filename} does not exist. Skipping...")
    #         continue
    #     if not filename.endswith(".csv"):
    #         print(f"File {filename} is not a CSV file. Skipping...")
    #         continue
    #     data = get_values(filename)
    #     # data.plot(kind='line', x='end_date', y='current_balance', ax=ax, label=filename, color=PALETTE[len(ax.lines) % len(PALETTE)])
    #     data.plot(kind='line', x='end_date', y='current_balance')


