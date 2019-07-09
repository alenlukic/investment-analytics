import argparse
import logging
import json
import requests
from enum import Enum
from os.path import join


CONFIG = json.load(open('config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.api.iex_api')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')
RAW_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'raw')

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


class Endpoint(Enum):
    """ Enumeration of API endpoints used in stock data ingestion. """

    ADVANCED_STATS = 'stock/%s/advanced-stats'
    CASH_FLOW = 'stock/%s/cash-flow'
    SYMBOLS = 'ref-data/symbols'


class IEXCloudAPI:
    """ Class encapsulating the IEX Cloud API. """

    def __init__(self, is_prod):
        """ Initializes class with API's base url and parameters (API token).

        Parameters:
            is_prod (boolean): indicates whether to use production endpoint.
        """

        self.base_url = CONFIG['API_URL'] if is_prod else CONFIG['SANDBOX_API_URL']
        self.params = {'token': CONFIG['API_KEY'] if is_prod else CONFIG['SANDBOX_API_KEY']}

    def get_advanced_stats(self, ticker):
        """ Make GET request to the /advanced-stats endpoint.

        Parameters:
            ticker (string): Ticker symbol for which to pull data.
        """

        request_url = join(self.base_url, Endpoint.ADVANCED_STATS.value % ticker)
        return self._get_response(request_url)

    def get_cash_flow(self, ticker):
        """ Make GET request to the /stock/cash-flow endpoint.

        Parameters:
            ticker (string): Ticker symbol for which to pull data.
        """

        request_url = join(self.base_url, Endpoint.CASH_FLOW.value % ticker)
        return self._get_response(request_url)

    def get_symbols(self):
        """ Make GET request to the /ref-data/symbols endpoint. """

        request_url = join(self.base_url, Endpoint.SYMBOLS.value)
        return self._get_response(request_url)

    def _get_response(self, request_url):
        """ Make GET request using the given URL, handle any errors, and return response content.

        Parameters:
            request_url (string): URL for which to make GET request.
        """

        try:
            response = requests.get(request_url, params=self.params)
            if response.status_code != 200:
                response_context = build_response_context(response)
                logging.warning('Got non-200 response while hitting %s: %s', request_url, json.dumps(response_context))
                return {}
            return json.loads(response.content or {})
        except Exception as e:
            logging.warning('The following exception occurred while hitting %s: %s', request_url, str(e))
            return {}


def build_response_context(response):
    """ Builds a dictionary containing useful API response data when a non-200 status code is received.

    Parameters:
        response (requests.Response): Response object
    """

    return {
        'Status': response.status_code,
        'Reason': response.reason,
        'Content': json.loads(response.content or {}),
        'Headers': json.loads(response.headers or {}),
        'Url': response.url
    }


def get_symbols(output_name='all_iex_supported_tickers.txt'):
    """ Gets JSON representation of all symbols supported on IEX Cloud.

    Parameters:
        output_name (str): file name in raw data directory where JSON dump should be saved.
    """

    output_path = join(RAW_DATA_DIR, output_name)
    symbol_json = API.get_symbols()
    symbols = sorted([t['symbol'] for t in filter(lambda j: j['type'] == 'cs', symbol_json)])
    with open(output_path, 'r') as output_file:
        output_file.write('\n'.join(symbols))


def ingest_stock_data(symbol_json='all_iex_supported_tickers.txt', output_name='stock_data_'):
    """ Ingests financial and technical indicator data for all actively traded stocks on NASDAQ.

    Parameters:
         symbol_json (string): file name in raw data directory containing IEX symbol JSON dump.
         output_name (string): base file name for partial stock data JSON dumps in processed data directory.
    """

    input_path = join(RAW_DATA_DIR, symbol_json)
    base_output_path = join(PROCESSED_DATA_DIR, output_name)

    with open(input_path, 'r') as input_file:
        symbols = [s.strip() for s in input_file.readlines()]
        symbol_data = {}
        n = len(symbols)

        for i, symbol in enumerate(symbols):
            print('Processing symbol %s (%d of %d)' % (symbol, i + 1, n))

            symbol_data[symbol] = {
                Endpoint.ADVANCED_STATS.name: API.get_advanced_stats(symbol),
                Endpoint.CASH_FLOW.name: API.get_cash_flow(symbol)
            }

            # Dump data in segments
            if (i + 1) % 10 == 0 or i == n - 1:
                with open(base_output_path + str(i + 1) + '.json', 'w') as output_file:
                    json.dump(symbol_data, output_file, indent=2, sort_keys=True)
                symbol_data = {}


def build_argument_parser():
    """ Build parser for command-line arguments. """

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--production', action='store_true')
    parser.add_argument('-s', '--symbols', action='store_true')

    return parser


if __name__ == '__main__':
    args = build_argument_parser().parse_args()
    API = IEXCloudAPI(args.production)
    if args.symbols:
        get_symbols()
    ingest_stock_data()
