import main
import pandas as pd
import numpy as np

def get_df(start_date = "2023-01-10", end_date = "2023-08-01"):
    #sp500 = main.fetch_dataframe_from_mongodb("finance_data", "sp500",
    #                                       start_date, end_date)
    nasdaq100 = main.fetch_dataframe_from_mongodb("finance_data", "nasdaq100",
                                           start_date, end_date)
    #russel2000 = main.fetch_dataframe_from_mongodb("finance_data", index,
    #                                       start_date, end_date)
    df = nasdaq100#pd.merge(sp500, nasdaq100, on = "date", how = "inner", suffixes = [None, "_y"])
    return df

df = get_df()
def get_most_correlated_pairs(df, num_pairs=5):
    correlation_matrix = df.corr()
    # Get the most correlated pairs
    most_correlated_pairs = correlation_matrix.unstack().abs().sort_values(ascending=False)[::2]
    most_correlated_pairs = most_correlated_pairs[most_correlated_pairs < 1]  # Exclude self-correlations
    most_correlated_pairs = most_correlated_pairs.head(num_pairs)

    spread = np.subtract(
        df[list(most_correlated_pairs.index.get_level_values(0))].to_numpy(),
        df[list(most_correlated_pairs.index.get_level_values(1))].to_numpy()
    )

    import statsmodels.api as sm
    def mean_rev(x):
        model = sm.OLS(x[1:], sm.add_constant(x[:-1]))
        results = model.fit()
        return results.params[1]

    mean_reversion = np.apply_along_axis(mean_rev, axis=0, arr=spread)


    return {"pairs" : most_correlated_pairs,
            "mean_reversion" : mean_reversion
            }

print(get_most_correlated_pairs(df))

def trade(stock1, stock2, capital = 1.0,
          lookback_period = 10, entry_threshold = 1.0, exit_threshold = 0.2):
    # Calculate the price ratio of the two stocks
    price_ratio = stock1 / stock2

    # Calculate z-score of the price ratio using a rolling window
    z_scores = (price_ratio - np.mean(price_ratio)) / np.std(price_ratio)

    # Initialize positions and portfolio value
    positions = np.zeros(len(price_ratio))
    portfolio_value = np.zeros(len(price_ratio))
    portfolio_value[0] = capital

    for t in range(lookback_period, len(price_ratio)):
        if z_scores[t] > entry_threshold:
            positions[t] = -1
        elif z_scores[t] < -entry_threshold:
            positions[t] = 1

        if abs(z_scores[t]) < exit_threshold:
            positions[t] = 0
        # Update portfolio value
        portfolio_value[t] = portfolio_value[t - 1] + positions[t] * (price_ratio[t] - price_ratio[t - 1])

    returns = np.diff(portfolio_value)
    def sortino(returns, risk_free_rate = 0, target_return=0):
        return (np.mean(returns) - risk_free_rate) / np.std(np.minimum(returns - target_return, 0))

    import matplotlib.pyplot as plt
    plt.plot(portfolio_value, "o")
    plt.axhline()
    plt.show()

    return {"positions" : pd.Series(positions, index=stock1.index),
            "value" : portfolio_value,
            "returns": returns,
            "sharpe" : np.mean(returns)/np.std(returns),
            "sortino" : sortino(returns)
            }


print(trade(df["AAPL"], df["MSFT"]))