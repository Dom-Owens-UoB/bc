import yfinance as yf
import pymongo
import pandas as pd

# Connect to the MongoDB server
client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["finance_data"]

def fetch_store_data(tickers, collection_name):
    collection = database[collection_name]
    database.drop_collection(collection)

    for ticker in tickers:
        # Fetch data using yfinance
        stock_data = yf.download(ticker, start="2023-01-01", end="2023-08-20")

        # Extract "Close" data from the DataFrame
        close_data = stock_data["Close"]

        # store data in collection
        for date, close in close_data.items():
            encoded_date = date.strftime('%Y-%m-%d')
            document_id = f"{encoded_date}_{ticker}"
            document = {"_id": document_id, "ticker": ticker, "date": encoded_date, "close": close}
            collection.insert_one(document)

        print(f"Stored close data for {ticker} in {collection_name}")



# List of tickers for S&P 500, Russell 2000, and Nasdaq 100
sp500_tickers = pd.read_html(
    'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]["Symbol"]
#russell2000_tickers =
nasdaq100_tickers = pd.read_html(
    'https://en.wikipedia.org/wiki/Nasdaq-100#Components')[4]["Ticker"]

# Fetch and store data for each index component
fetch_store_data(sp500_tickers, "sp500")
#fetch_store_data(russell2000_tickers, "russell2000")
fetch_store_data(nasdaq100_tickers, "nasdaq100")

# Fetch and store index data
index_tickers = ["^GSPC", "^RUT", "^IXIC"]  # S&P 500, Russell 2000, Nasdaq 100
fetch_store_data(index_tickers, "indices")





def fetch_dataframe_from_mongodb(database_name, collection_name, start_date, end_date):
    # Connect to the MongoDB server
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    database = client[database_name]
    collection = database[collection_name]

    # Fetch all documents from the collection
    query = {"date": {"$gte": start_date, "$lte": end_date}}
    cursor = collection.find(query)

    # Convert documents to a list of dictionaries
    documents = list(cursor)

    # Convert list of dictionaries to a DataFrame
    dataframe = pd.DataFrame(documents)

    # pivot on columns
    pivoted_dataframe = dataframe.pivot(index= "date", columns="ticker", values="close")

    # Close the MongoDB connection
    client.close()

    return pivoted_dataframe

