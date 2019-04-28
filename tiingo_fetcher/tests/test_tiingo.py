import os

from tiingo import TiingoClient

api_key = os.environ.get("TIINGO_API_KEY")
config = {}

# To reuse the same HTTP Session across API calls (and have better performance), include a session key.
config['session'] = True

# If you don't have your API key as an environment variable,
# pass it in via a configuration dictionary.
config['api_key'] = api_key

# Initialize
client = TiingoClient(config)



def test_call_tiingo():
    prices = client.get_ticker_price("AAPL", startDate="1800-1-1", frequency="daily", fmt="csv")

    for price in prices:
        print(price)
    assert len(prices) < 0