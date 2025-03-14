import random

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def pretty_line_chart(series_one, series_two, *args):
    plt.figure(figsize=(16,10), dpi=80)
    plt.plot(series_one.index, series_one.values, color='tab:red', label="Mean Reversal Portfolio")
    plt.plot(series_two.index, series_two.values, color='blue', label = "SPY")  # New line to plot series_two in blue

    # For plotting variable random tests
    random_rgb = lambda: (random.random(), random.random(), random.random())
    i = 1
    for arg in args:
        to_label = f"Random Portfolio {i}"
        plt.plot(series_one.index, arg.values, color=random_rgb(), label=to_label)
        i += 1

    # Decoration: adjust the y-limits as needed
    global_min = min(series_one.min(), series_two.min())
    global_max = max(series_one.max(), series_two.max())
    plt.ylim(global_min * 0.90, global_max * 1.10)

    # Create xtick locations from the index (every 12th date)
    xtick_locations = series_one.index[::12]

    # Set the x-axis to use one tick per month
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Use '%b' for abbreviated month name

    plt.title("Comparison of Mean Reversal Portfolio to SPY", fontsize=22)
    plt.grid(axis='both', alpha=0.3)

    # Remove borders
    ax.spines["top"].set_alpha(0.0)
    ax.spines["bottom"].set_alpha(0.3)
    ax.spines["right"].set_alpha(0.0)
    ax.spines["left"].set_alpha(0.3)

    plt.legend(loc="upper left", fontsize=16)
    plt.show()


def import_and_filter_csv(path_to_csv):
    """
    Imports a CSV file and filters the data for dates between Jan 1, 2020 and Dec 31, 2024.

    Parameters:
        path_to_csv (str): The path to the CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing only the data within the specified date range.
    """
    # Read the CSV file and parse the "Date" column as datetime
    df = pd.read_csv(path_to_csv, parse_dates=["Date"])

    # Define the start and end dates
    start_date = pd.to_datetime("2020-01-02")
    end_date = pd.to_datetime("2023-12-1")

    # Filter the DataFrame for dates within the specified range
    mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
    filtered_df = df.loc[mask].reset_index(drop=True)

    # print("THIS IS WHAT FILTERED_DF LOOKS LIKE RIGHT NOW!!!!")
    # print(filtered_df)

    # print("Multiplication Scale to have 1000000 in SPY on day 1:")
    to_multiply = 1000000 / filtered_df['Close'][0]
    # print(to_multiply)

    # print("After Normalization:")
    filtered_df['Close'] = to_multiply * filtered_df['Close']
    # print(filtered_df.to_string(float_format=lambda x: f'{x:.2f}'))

    return filtered_df


def df_to_close_series(df):
    """
    Converts a DataFrame to a date-indexed Series containing only the 'Close' values.

    Parameters:
        df (pd.DataFrame): DataFrame that contains at least 'Date' and 'Close' columns.

    Returns:
        pd.Series: A series with dates as the index and 'Close' values.
    """
    # Ensure a copy is made so the original DataFrame isn't modified
    df_copy = df.copy()

    # Set 'Date' as the index
    df_copy.set_index('Date', inplace=True)

    # Return the 'Close' column as a Series
    close_series = df_copy['Close']
    return close_series