import argparse
import logging
import json
import requests
from enum import Enum
from os.path import join


CONFIG = json.load(open('../../config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.api.iex_api')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')
RAW_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'raw')

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


class Endpoint(Enum):
    """ Enumeration of API endpoints used in stock data ingestion. """

    ADVANCED_STATS = 'stock/%s/advanced-stats'
    CASH_FLOW = 'stock/%s/cash-flow'
    DIVIDENDS = 'stock/%s/dividends/%s'
    EARNINGS = 'stock/%s/earnings/%s'
    FINANCIALS = 'stock/%s/financials'
    HISTORICAL_PRICES = 'stock/%s/chart/%s'
    INCOME = 'stock/%s/income'


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
        """ Make GET request to the /cash-flow endpoint.

        Parameters:
            ticker (string): Ticker symbol for which to pull data.
        """

        request_url = join(self.base_url, Endpoint.CASH_FLOW.value % ticker)
        return self._get_response(request_url)

    def get_dividends(self, ticker, time_range='1y'):
        """ Make GET request to the /dividends endpoint.

        Parameters:
            ticker (string): Ticker symbol for which to pull data.
            time_range (string): Period for which to pull data.
        """

        request_url = join(self.base_url, Endpoint.DIVIDENDS.value % (ticker, time_range))
        return self._get_response(request_url)

    def get_earnings(self, ticker, quarters='4'):
        """ Make GET request to the /earnings endpoint.

        Parameters:
            ticker (string): Ticker symbol for which to pull data.
            quarters (string): Number of quarters for which to pull data.
        """

        request_url = join(self.base_url, Endpoint.EARNINGS.value % (ticker, quarters))
        return self._get_response(request_url)

    def get_financials(self, ticker):
        """ Make GET request to the /financials endpoint.

        Parameters:
            ticker (string): Ticker symbol for which to pull data.
        """

        request_url = join(self.base_url, Endpoint.FINANCIALS.value % ticker)
        return self._get_response(request_url)

    def get_historical_prices(self, ticker, time_range='1y'):
        """ Make GET request to the /chart endpoint.

        Parameters:
            ticker (string): Ticker symbol for which to pull data.
            time_range (string): Period for which to pull data.
        """

        request_url = join(self.base_url, Endpoint.HISTORICAL_PRICES.value % (ticker, time_range))
        return self._get_response(request_url)

    def get_income(self, ticker):
        """ Make GET request to the /income endpoint.

        Parameters:
            ticker (string): Ticker symbol for which to pull data.
        """

        request_url = join(self.base_url, Endpoint.INCOME.value % ticker)
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


def ingest_stock_data(is_prod, tickers='all_iex_supported_tickers.json', output_name='stock_data_'):
    """ Ingests financial and technical indicator data for all actively traded stocks on NASDAQ. """

    input_path = join(RAW_DATA_DIR, tickers)
    base_output_path = join(PROCESSED_DATA_DIR, output_name)

    with open(input_path, 'r') as input_file:
        ticker_json = json.load(input_file)
        symbols = [t['symbol'] for t in filter(lambda j: j['type'] == 'cs', ticker_json)]
        n = len(symbols)
        symbol_data = {}
        api = IEXCloudAPI(is_prod)

        for i, symbol in enumerate(symbols):
            print('Processing symbol %s (%d of %d)' % (symbol, i + 1, n))

            symbol_data[symbol] = {
                Endpoint.ADVANCED_STATS.name: api.get_advanced_stats(symbol),
                Endpoint.CASH_FLOW.name: api.get_cash_flow(symbol)
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

    return parser


if __name__ == '__main__':
    args = build_argument_parser().parse_args()
    ingest_stock_data(args.production)
