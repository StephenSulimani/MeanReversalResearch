import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cvxpy as cp
import json
import os


from pypfopt import risk_models

# Step 0: Iterate over all time periods

# Open and store the array in runs.json
if os.path.exists("runs.json"):
    with open("runs.json", "r") as file:
        runs = json.load(file)
else:
    runs = []

stocks_to_long = []
stocks_to_short = []

# print(f"runs: {runs[0]}")
# for i in range(min(10, len(runs))):
for i in range(0, len(runs)):
    print(f"Item {i}: {runs[i]}")

    # Print the items to long and the items to short
    stocks_to_long = runs[i]["worst_stocks"]
    stocks_to_short = runs[i]["best_stocks"]
    tickers = stocks_to_long + stocks_to_short
    print(f"Stocks to long: {stocks_to_long}")
    print(f"Stocks to short: {stocks_to_short}")

    start_date = runs[i]["lookback"]["start"]
    end_date = runs[i]["test"]["end"]

    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")

    # pull the close price of each stock in the list
    prices = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date))


    for ticker in stocks_to_long + stocks_to_short:
        # Load the data from local CSV files in the data/{ticker} directory
        file_path = f"data/{ticker}.csv"
        if os.path.exists(file_path):
            # data = pd.read_csv(file_path, parse_dates=["Date"], index_col="Date")
            data = pd.read_csv(file_path, parse_dates=True, index_col="date")
            # Append the close price to the dataframe
            prices[ticker] = data["close"]
        else:
            print(f"Data for {ticker} not found in {file_path}")


    # Check if prices DataFrame is empty
    prices.dropna(inplace=True)
    print(prices.head(10))
    print()

    # Checkpoint: At this point, we have all of our price data in the prices DataFrame

    # Step 1: Estimate risk (covariance matrix)
    sample_cov = risk_models.sample_cov(prices, frequency=252)

    # Step 2: Define alpha signal (mean reversion)
    mu = pd.Series(
        data=[1.0] * len(stocks_to_long) + [-1.0] * len(stocks_to_short),
        index=tickers
    )

    # Step 3: Setup optimization using cvxpy
    n = len(tickers)
    w = cp.Variable(n)  # weights to solve for

    # Constraints
    constraints = [
        cp.sum(w) == 0,               # Dollar neutral
        cp.norm1(w) <= 1              # Leverage limit
    ]
        
    # Optional: enforce long and short positions based on user input
    for j, ticker in enumerate(tickers):
        if ticker in stocks_to_long:
            constraints.append(w[j] >= 0)
        elif ticker in stocks_to_short:
            constraints.append(w[j] <= 0)

    # Objective function: maximize return - λ * risk
    expected_returns_vector = mu.values
    cov_matrix = sample_cov.loc[tickers, tickers].values

    lambda_risk_aversion = 0.02  # risk penalty (tune this)
    portfolio_return = expected_returns_vector @ w
    portfolio_risk = cp.quad_form(w, cov_matrix)

    objective = cp.Maximize(portfolio_return - lambda_risk_aversion * portfolio_risk)
    # objective = cp.Maximize(0 - lambda_risk_aversion * portfolio_risk)
    problem = cp.Problem(objective, constraints)
    problem.solve()

    # Step 4: Output results
    weights = pd.Series(w.value, index=tickers)
    weights = weights.round(4)

    print("\nOptimal Dollar-Neutral Weights:")
    print(weights)

    runs[i]["weights"] = weights.to_dict()

    print(f"\nSum of weights (should be ~0): {weights.sum():.6f}")
    print(f"Gross exposure (L1 norm): {np.abs(weights).sum():.4f}")



    # Step 5: Visualize --> Unncomment this if you want to see individual weights for each run
#     weights.plot(kind="bar", title="Dollar-Neutral Portfolio Weights for Lookback Period " + str(i))
#     plt.axhline(0, color='black', linewidth=0.8)
#     plt.ylabel("Weight")
#     plt.tight_layout()
#     # plt.show()

# # Save the updated runs array back to weighted_runs.json
with open("weighted_runs.json", "w") as file:
    json.dump(runs, file, indent=4)