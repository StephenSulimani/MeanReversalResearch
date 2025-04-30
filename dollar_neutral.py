import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cvxpy as cp

from pypfopt import risk_models

# Load price data
prices = pd.read_csv("stuff/historical_prices.csv", index_col="Date", parse_dates=True)

# Define long/short groups
stocks_to_long = ["COST", "LUV", "XOM", "TSLA"]
stocks_to_short = ["MSFT", "AMZN", "KO", "MA"]
tickers = stocks_to_long + stocks_to_short

# Restrict to the tickers we're using
prices = prices[tickers]

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
for i, ticker in enumerate(tickers):
    if ticker in stocks_to_long:
        constraints.append(w[i] >= 0)
    elif ticker in stocks_to_short:
        constraints.append(w[i] <= 0)

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

print("\nOptimal Dollar-Neutral Weights:")
print(weights)
print(f"\nSum of weights (should be ~0): {weights.sum():.6f}")
print(f"Gross exposure (L1 norm): {np.abs(weights).sum():.4f}")

# Step 5: Visualize
weights.plot(kind="bar", title="Dollar-Neutral Portfolio Weights")
plt.axhline(0, color='black', linewidth=0.8)
plt.ylabel("Weight")
plt.tight_layout()
plt.show()
