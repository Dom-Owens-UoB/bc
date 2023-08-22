import main

## regression
def regression(cols, index = "nasdaq100", start_date = "2023-01-10", end_date = "2023-08-01"):
     assert len(cols)<=10, "give 10 or fewer assets"

     index_tickers = {"sp500" : "^GSPC", "russel2000": "^RUT", "nasdaq100": "^IXIC"}
     df = main.fetch_dataframe_from_mongodb("finance_data", index,
                                       start_date, end_date)
     ind = main.fetch_dataframe_from_mongodb("finance_data", "indices",
                                       start_date, end_date)

     import statsmodels.api as sm
     x = df[cols]
     y = ind[index_tickers[index]]
     mod = sm.OLS(y, x)
     res = mod.fit()
     print(res.summary())
     import matplotlib.pyplot as plt
     plt.plot(y, res.fittedvalues, "o")
     plt.show()



regression(["AAPL", "MSFT"])



## subset selection
from sklearn.decomposition import PCA
import pandas as pd
def subset(index = "nasdaq100", n_tickers = 10, start_date = "2023-01-10", end_date = "2023-08-01"):
     df = main.fetch_dataframe_from_mongodb("finance_data", index,
                                       start_date, end_date)
     correlation_matrix = df.corr()
     pca = PCA(n_components=1)
     principal_component = pca.fit_transform(correlation_matrix)

     # Convert the principal component array to a DataFrame
     principal_df = pd.DataFrame(principal_component, index=correlation_matrix.index, columns=["pc"])

     # Get the n_tickers most correlated tickers
     most_correlated_tickers = principal_df.abs().sort_values(by = "pc", ascending=False).head(n_tickers)

     return most_correlated_tickers

print(subset())


