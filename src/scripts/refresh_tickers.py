import json

from src.api.stock_data_api import IEXCloudAPI
from src.definitions.config import TICKER_TARGET


def refresh_tickers():
    api = IEXCloudAPI(False)
    ticker_data = list(filter(lambda j: j['type'] == 'cs', api.get_symbols()))
    symbol_string = '\n'.join([t['symbol'] for t in ticker_data])

    with open(TICKER_TARGET + '.json', 'w') as jf:
        json.dump(ticker_data, jf, indent=2)

    with open(TICKER_TARGET + '.txt', 'w') as tf:
        tf.write(symbol_string)


if __name__ == '__main__':
    refresh_tickers()
