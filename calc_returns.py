from stooq import Stooq


def calc_short_return(ticker, start_date, end_date):
    """
    Function to calculate the return of a short stock trade in percentage terms.
    """
    # Download stock data
    stock = Stooq.download(ticker, start_date, end_date)

    # Ensure data is available
    if stock.empty:
        print("No data available for the given date range.")
        return None

    # Select short and cover dates (first & last available trading days)
    short_date = stock.index[0]  # First trading day
    cover_date = stock.index[-1]  # Last trading day

    # Get stock prices
    short_price = stock.loc[short_date, 'Open']
    cover_price = stock.loc[cover_date, 'Close']

    # Calculate Short Return as a Percentage
    percent_return = ((short_price - cover_price) / short_price) * 100

    # Display results
    result = {
        "Short Date": short_date.date(),
        "Short Price ($)": round(short_price, 2),
        "Cover Date": cover_date.date(),
        "Cover Price ($)": round(cover_price, 2),
        "Short Return (%)": round(percent_return, 2)
    }

    for key, value in result.items():
        print(f"\t{key}: {value}")

def calc_long_return(ticker, start_date, end_date):
    """
    Function to calculate the return of a long stock trade in percentage terms.
    """
    # Download stock data
    stock = Stooq.download(ticker, start_date, end_date)

    # Ensure data is available
    if stock.empty:
        print("No data available for the given date range.")
        return None

    # Select short and cover dates (first & last available trading days)
    buy_date = stock.index[0]  # First trading day
    sell_date = stock.index[-1]  # Last trading day

    # Get stock prices
    buy_price = stock.loc[buy_date, 'Open']
    sell_price = stock.loc[sell_date, 'Close']

    # Calculate Short Return as a Percentage
    percent_return = ((sell_price - buy_price) / buy_price) * 100

    # Plot stock price
    # plot_stock_price(stock, short_date, cover_date, short_price, cover_price)

    # Display results
    result = {
        "Buy Date": buy_date.date(),
        "Buy Price ($)": round(buy_price, 2),
        "Sell Date": sell_date.date(),
        "Sell Price ($)": round(sell_price, 2),
        "Long Return (%)": round(percent_return, 2)
    }

    for key, value in result.items():
        print(f"\t{key}: {value}")


# Example usage
if __name__ == "__main__":
    # short_stock_return("AAPL", "2023-08-13", "2024-02-13")
    print("Example Usage:")
    print("Short on AAPL from 2023-08-13 to 2024-02-13")
    calc_short_return("AAPL", "20230813", "20240213")
    print("\nLong on GOOG from 2023-08-13 to 2024-02-13")
    calc_long_return("GOOG", "20230813", "20240213")
