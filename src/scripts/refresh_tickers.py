import json

from src.api.stock_data_api import IEXCloudAPI
from src.definitions.config import TICKER_DETAILS, TICKER_SYMBOLS


def refresh_tickers():
    api = IEXCloudAPI(False)
    ticker_data = list(filter(lambda j: j['type'] == 'cs', api.get_symbols()))
    symbol_string = '\n'.join([t['symbol'] for t in ticker_data])

    with open(TICKER_DETAILS, 'w') as jf:
        json.dump(ticker_data, jf, indent=2)

    with open(TICKER_SYMBOLS, 'w') as tf:
        tf.write(symbol_string)

    """
    Symbol filtering
    
    - De-duplicate (e.g. stock splits, stock categories)
    - Remove bankrupt and delisted stocks
    """


if __name__ == '__main__':
    refresh_tickers()
