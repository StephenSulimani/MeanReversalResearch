import json
import sys

import pandas as pd


def get_stock_price(ticker: str, date: pd.Timestamp, backward=True) -> float:
    # 1) Load & index
    stock_df = pd.read_csv("data/" + ticker + ".csv", parse_dates=["date"])
    stock_df.set_index("date", inplace=True)

    # 2) Drop duplicate dates (keep first) so loc[...] returns a single row
    stock_df = stock_df[~stock_df.index.duplicated(keep="first")]

    # 3) Determine your data bounds
    min_date = stock_df.index.min()
    max_date = stock_df.index.max()

    # 4) Clamp the requested date into [min_date, max_date]
    if date < min_date:
        date = min_date
    elif date > max_date:
        date = max_date

    # 5) Walk day‐by‐day until we hit an available date
    while date not in stock_df.index:
        if backward:
            date -= pd.Timedelta(days=1)
            if date < min_date:
                date = min_date
                break
        else:
            date += pd.Timedelta(days=1)
            if date > max_date:
                date = max_date
                break

    # 6) Grab the close price (if you somehow still get a Series, take the first)
    price = stock_df.loc[date, "close"]
    if isinstance(price, pd.Series):
        price = price.iloc[0]

    return float(price)


def run_backtest(portfolio_json, starting_capital, csv_filename):
    original_capital = starting_capital
    current_balance = starting_capital
    output_df = pd.DataFrame(columns=["start_date", "end_date", "current_balance", "monthly_change"])
    for i, breakpoint in enumerate(portfolio_json):
        prev_balance = current_balance
        new_balance = current_balance
        holdings = {}
        test_dates = breakpoint["test"]
        start_date = pd.to_datetime(test_dates["start"])
        end_date = pd.to_datetime(test_dates["end"])

        if i == 0:
            output_df = output_df._append({
                'start_date': '--',
                'end_date': (start_date - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                'current_balance': starting_capital,
                'monthly_change': 0
            }, ignore_index=True)

        weights_exist = breakpoint.get("weights", None)
        if weights_exist is None:
            weight = 1.0 / len(breakpoint["best_stocks"])
            for ticker in breakpoint["best_stocks"]:
                price = get_stock_price(ticker, start_date, False)
                holdings[ticker] = {
                    "amount": (current_balance * weight) / price,
                    "initial_price": price,
                }
            weight = (1.0 / len(breakpoint["worst_stocks"])) * -1.0
            for ticker in breakpoint["worst_stocks"]:
                price = get_stock_price(ticker, start_date, False)
                holdings[ticker] = {
                    "amount": (current_balance * weight) / price,
                    "initial_price": price,
                }


        else:
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

        output_df = output_df._append(
                {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "current_balance": current_balance,
                    "monthly_change": portfolio_json[i]["backtest"]["change_pct"],
                }, ignore_index=True
        )
        output_df.to_csv(csv_filename, index=False)
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
    if len(sys.argv) != 4:
        print("Usage: python Backtester.py <json_file> <starting_capital> <output_csv>")
        sys.exit(1)

    portfolio_json = json.load(open(sys.argv[1], "r"))
    starting_capital = float(sys.argv[2])
    output_csv = sys.argv[3]

    run_backtest(portfolio_json, starting_capital, output_csv)
