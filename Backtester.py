import json
import sys

import pandas as pd


def get_stock_price(ticker: str, date: pd.DatetimeIndex, backward=True) -> float:
    stock_df = pd.read_csv("data/" + ticker + ".csv", parse_dates=["date"])
    stock_df.set_index("date", inplace=True)

    while date not in stock_df.index:
        if backward:
            date -= pd.Timedelta(days=1)
        else:
            date += pd.Timedelta(days=1)

    return stock_df.loc[date]["close"]


def run_backtest(portfolio_json, starting_capital):
    original_capital = starting_capital
    current_balance = starting_capital
    for i, breakpoint in enumerate(portfolio_json):
        prev_balance = current_balance
        new_balance = current_balance
        holdings = {}
        test_dates = breakpoint["test"]
        start_date = pd.to_datetime(test_dates["start"])
        end_date = pd.to_datetime(test_dates["end"])

        for ticker, weight in breakpoint["weights"].items():
            weight = float(weight)
            price = get_stock_price(ticker, start_date, False)

            holdings[ticker] = {
                "amount": (current_balance * weight) / price,
                "initial_price": price,
            }

        for ticker, info in holdings.items():
            amount = info["amount"]
            initial_price = info["initial_price"]
            end_price = get_stock_price(ticker, end_date)
            if amount > 0:
                gross = amount * (end_price - initial_price)
                new_balance += gross  # Long Position
            elif amount < 0:
                gross = amount * (initial_price - end_price)
                new_balance += gross  # Short Position

        portfolio_json[i]["backtest"] = {
            "starting_bal": prev_balance,
            "new_bal": new_balance,
            "change_pct": (
                ((new_balance - prev_balance) / prev_balance * 100)
                if prev_balance != 0
                else None
            ),
        }

        current_balance = new_balance

        print()
        print(f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"Starting Balance: {prev_balance}")
        print(f"New Balance: {current_balance}")
        print(f"Change %: {portfolio_json[i]['backtest']['change_pct']}")
        print(f"Progress: {i + 1}/{len(portfolio_json)}")
        print()
    final_capital = current_balance

    print("Starting Capital: ", original_capital)
    print("Final Capital: ", final_capital)
    print("Change %: ", (final_capital - original_capital) / original_capital * 100)


def old_run_backtest(portfolio_json, starting_capital):
    current_balance = starting_capital
    for i, breakpoint in enumerate(portfolio_json):
        prev_balance = current_balance
        new_bal = 0
        holdings = {}
        test_dates = breakpoint["test"]
        start_date = pd.to_datetime(test_dates["start"])
        end_date = pd.to_datetime(test_dates["end"])

        for ticker, weight in breakpoint["weights"].items():
            weight = float(weight)
            price = get_stock_price(ticker, start_date, False)

            holdings[ticker] = {
                "amount": (current_balance * weight) / price,
                "initial_price": price,
            }
        for ticker, info in holdings.items():
            amount = info["amount"]
            initial_price = info["initial_price"]
            end_price = get_stock_price(ticker, end_date)
            if amount > 0:
                # print("LONG")
                # print("Start Price: ", initial_price)
                # print("End Price: ", end_price)
                # print("Amount: ", amount)
                # print("P/L:", amount * end_price - amount * initial_price)
                # input()
                new_bal += amount * end_price
                # Long Position
            else:
                # print("SHORT")
                # print("Start Price: ", initial_price)
                # print("End Price: ", end_price)
                # print("Amount: ", amount)
                short_sale_proceeds = abs(amount) * initial_price
                cost_to_close = abs(amount) * end_price
                # print("P/L:", short_sale_proceeds - cost_to_close)
                # input()
                new_bal += short_sale_proceeds - cost_to_close
                # Short Position

        portfolio_json[i]["backtest"] = {
            "starting_bal": prev_balance,
            "new_bal": new_bal,
            "change_pct": (new_bal - prev_balance) / prev_balance * 100,
        }

        current_balance = new_bal

        print()
        print(f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"Starting Balance: {prev_balance}")
        print(f"New Balance: {current_balance}")
        print(f"Change %: {portfolio_json[i]['backtest']['change_pct']}")
        print(f"Progress: {i + 1}/{len(portfolio_json)}")
        print()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Backtester.py <json_file> <starting_capital>")
        sys.exit(1)

    portfolio_json = json.load(open(sys.argv[1], "r"))
    starting_capital = float(sys.argv[2])

    run_backtest(portfolio_json, starting_capital)
