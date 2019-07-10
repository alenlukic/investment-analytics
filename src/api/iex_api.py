import argparse
import logging
import json
import requests
from datetime import datetime
from enum import Enum
from os import makedirs
from os.path import join

from src.utils.data_utils import merge_stock_data
from src.utils.file_utils import save_file, save_json


CONFIG = json.load(open('config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.api.iex_api')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')
RAW_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'raw')

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


ENDPOINT_TO_FUNCTION = {
    'ADVANCED_STATS': 'get_advanced_stats',
    'CASH_FLOW': 'get_cash_flow',
    'PRICE': 'get_price'
}


class Endpoint(Enum):
    """ Enumeration of API endpoints used in stock data ingestion. """

    ADVANCED_STATS = 'stock/%s/advanced-stats'
    CASH_FLOW = 'stock/%s/cash-flow'
    PRICE = 'stock/%s/price'
    SYMBOLS = 'ref-data/symbols'


class IEXCloudAPI:
    """ Class encapsulating the IEX Cloud API. """

    def __init__(self, is_prod):
        """ Initializes class with API's base url and parameters (API token).

        :param is_prod: indicates whether to use production endpoint.
        """

        self.base_url = CONFIG['API_URL'] if is_prod else CONFIG['SANDBOX_API_URL']
        self.params = {'token': CONFIG['API_KEY'] if is_prod else CONFIG['SANDBOX_API_KEY']}

    def get_function(self, function_name):
        """ Returns specified class function.

        :param function_name: Name of the function.
        :return: The function object.
        """

        return self.__getattribute__(function_name)

    def get_advanced_stats(self, ticker):
        """ Make GET request to the /stock/advanced-stats endpoint.

        :param ticker: Ticker symbol for which to pull data.
        :return: dictionary containing all keys in /stock/advanced-stats.
        """

        request_url = join(self.base_url, Endpoint.ADVANCED_STATS.value % ticker)
        return self._get_response(request_url)

    def get_cash_flow(self, ticker):
        """ Make GET request to the /stock/cash-flow endpoint.

        :param ticker: Ticker symbol for which to pull data.
        :return: dictionary containing all keys in /stock/cash-flow.
        """

        request_url = join(self.base_url, Endpoint.CASH_FLOW.value % ticker)
        return self._get_response(request_url)

    def get_price(self, ticker):
        """ Make GET request to the /stock/{symbol}/price endpoint.

        :param ticker: Ticker symbol for which to pull data.
        :return: number representing most recent stock price.
        """

        request_url = join(self.base_url, Endpoint.PRICE.value % ticker)
        return self._get_response(request_url)

    def get_symbols(self):
        """ Make GET request to the /ref-data/symbols endpoint.

        :return: dictionary containing information about all symbols supported by IEX.
        """

        request_url = join(self.base_url, Endpoint.SYMBOLS.value)
        return self._get_response(request_url)

    def _get_response(self, request_url):
        """ Make GET request using the given URL, handle any errors, and return response content.

        :param request_url: URL for which to make GET request.
        :return: the response content.
        """

        try:
            response = requests.get(request_url, params=self.params)
            if response.status_code != 200:
                response_context = self.error_response_context(response)
                logging.warning('Got non-200 response while hitting %s: %s', request_url, json.dumps(response_context))
                return {}
            return json.loads(response.content or {})
        except Exception as e:
            logging.warning('The following exception occurred while hitting %s: %s', request_url, str(e))
            return {}

    def _error_response_context(self, response):
        """ Builds a dictionary containing useful API response data when a non-200 status code is received.

        :param response: Response object.
        :return: dictionary containing response context.
        """

        return {
            'Status': response.status_code,
            'Reason': response.reason,
            'Content': json.loads(response.content or {}),
            'Headers': json.loads(response.headers or {}),
            'URL': response.url,
            'Prod?': self.is_prod
        }


def download_symbols(output_name='all_iex_supported_tickers.txt'):
    """ Gets JSON representation of all symbols supported on IEX Cloud.

    :param output_name: file name in raw data directory where JSON dump should be saved.
    """

    symbol_json = API.get_symbols()
    symbols = sorted([t['symbol'] for t in filter(lambda j: j['type'] == 'cs', symbol_json)])
    save_file(RAW_DATA_DIR, output_name, '\n'.join(symbols))


def ingest_stock_data(endpoints, symbol_json='all_iex_supported_tickers.txt', output_name='stock_data_'):
    """ Ingests financial and technical indicator data for all actively traded stocks on NASDAQ.

    :param endpoints: endpoints to hit during ingestion.
    :param symbol_json: file name in raw data directory containing IEX symbol JSON dump.
    :param output_name: base file name for partial stock data JSON dumps in processed data directory.
    """

    input_path = join(RAW_DATA_DIR, symbol_json)
    output_dir = join(PROCESSED_DATA_DIR, datetime.today().strftime('%Y%m%d'))
    makedirs(output_dir)

    with open(input_path, 'r') as input_file:
        symbols = [s.strip() for s in input_file.readlines()]
        symbol_data = {}
        n = len(symbols)

        for i, symbol in enumerate(symbols):
            print('Processing symbol %s (%d of %d)' % (symbol, i + 1, n))

            # symbol_data[symbol] = {
            #     Endpoint.ADVANCED_STATS.name: API.get_advanced_stats(symbol),
            #     Endpoint.CASH_FLOW.name: API.get_cash_flow(symbol)
            # }
            symbol_data[symbol] = {e: API.get_function(ENDPOINT_TO_FUNCTION[e])(symbol) for e in endpoints}

            # Dump data in segments
            if (i + 1) % 10 == 0 or i == n - 1:
                save_json(output_dir, output_name + str(i + 1) + '.json', symbol_data, True)
                symbol_data = {}

    merge_stock_data(output_dir)


def build_argument_parser():
    """ Build parser for command-line arguments.

    :return: argument parser object.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--production', action='store_true')
    parser.add_argument('-s', '--symbols', action='store_true')
    parser.add_argument('-e', '--endpoints', type=str, default='ADVANCED_STATS,CASH_FLOW,PRICE')

    return parser


if __name__ == '__main__':
    args = build_argument_parser().parse_args()
    API = IEXCloudAPI(args.production)
    if args.symbols:
        download_symbols()
    ingest_stock_data(args.endpoints.split(','))
