import argparse
import logging
import requests
from datetime import datetime
from enum import Enum

from src.definitions.config import *
from src.utils.data_utils import merge_stock_data_partials
from src.utils.file_utils import create_directory, save_file, save_json


logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


class StockDataAPI:
    """ Base class for any API used to obtain stock data. """

    def __init__(self, base_url, is_prod=True):
        self.base_url = base_url
        self.is_prod = is_prod

    def _get_response(self, request_url, params={}, headers={}, verify=True):
        """ Make GET request using the given URL, handle any errors, and return response.

        :param request_url: URL for which to make GET request.
        :return: the response.
        """

        try:
            response = requests.get(request_url, params=params, headers=headers, verify=verify)
            if response.status_code == 200:
                return response
            response_context = self._error_response_context(response)
            logging.warning('Got non-200 response while hitting %s: %s', request_url, json.dumps(response_context))
            return None
        except Exception as e:
            logging.warning('The following exception occurred while hitting %s: %s', request_url, str(e))
            return None

    def _error_response_context(self, response):
        """ Builds a dictionary containing useful API response data when a non-200 status code is received.

        :param response: Response object.
        :return: dictionary containing response context.
        """
        return {
            'Status': response.status_code,
            'Reason': response.reason,
            'Content': response.text,
            'Headers': json.loads(response.headers or {}),
            'URL': response.url,
            'Prod?': self.is_prod
        }


class FinancialContentAPI(StockDataAPI):
    """ Class encapsulating API requests to Financial Content. """

    class FinancialContentEndpoint(Enum):
        """ FC data endpoints. """
        DETAILED_QUOTE = 'quote/detailedquote'
        HISTORICAL_DATA = 'action/gethistoricaldata'

    # Maps endpoint name to function name used to hit that endpoint
    ENDPOINT_FUNCTIONS = {
        FinancialContentEndpoint.DETAILED_QUOTE.name: 'quote/detailedquote',
        FinancialContentEndpoint.HISTORICAL_DATA.name: 'action/gethistoricaldata',
    }

    def __init__(self):
        """ Initializes class with Financial Content's base url. """
        StockDataAPI.__init__(self, CONFIG['FINANCIAL_CONTENT_API_URL'])

    def get_detailed_quote(self, symbol):
        """ Make GET request to the quote/detailedquote endpoint.

        :param symbol: ticker symbol for which to pull data.
        :return: HTML page containing various ticker metrics.
        """

        params = {'Symbol': 'NY:' + symbol}
        endpoint = self.FinancialContentEndpoint.DETAILED_QUOTE.value
        referer_url = self._generate_referer_url(endpoint, params)
        headers = {'Upgrade-Insecure-Requests': '1', 'Referer': referer_url}

        return self._get_response(join(self.base_url, endpoint), params, headers)

    def get_historical_data(self, symbol, year, month, num_months=12):
        """ Make GET request to the action/gethistoricaldata endpoint.

        :param symbol: ticker symbol for which to pull data.
        :param year: end year for which to get data (last day of month).
        :param month: end month for which to get data.
        :param num_months: number of months for which to get data, ending at input year and month.
        :return: CSV of historical price data.
        """

        params = {'Symbol': 'NY:' + symbol, 'Year': year, 'Month': month, 'Range': num_months}
        endpoint = self.FinancialContentEndpoint.HISTORICAL_DATA.value
        referer_url = self._generate_referer_url(endpoint, params)
        headers = {'Upgrade-Insecure-Requests': '1', 'Referer': referer_url}

        return self._get_response(join(self.base_url, endpoint), params, headers)

    def _generate_referer_url(self, endpoint, params):
        """ Generates referer URL needed to make request to FC.

        :param endpoint: endpoint to hit.
        :param params: request parameters.
        :return: the referer URL.
        """
        param_str = '?' + '&'.join([(k + '=' + v).replace(':', '%3A') for k, v in params.items()])
        return join(self.base_url, endpoint + param_str)

    def _get_response(self, request_url, params={}, headers={}, verify=False):
        """ Make GET request using the given URL, handle any errors, and return response content.

        :param request_url: URL for which to make GET request.
        :return: the response content.
        """
        response = StockDataAPI._get_response(self, request_url, params, headers, verify)
        return (response and response.text) or ''


class IEXCloudAPI(StockDataAPI):
    """ Class encapsulating IEX Cloud API. """

    class IEXStockDataEndpoint(Enum):
        """ Stock data API endpoints. """

        ADVANCED_STATS = 'stock/%s/advanced-stats'
        CASH_FLOW = 'stock/%s/cash-flow'
        PRICE = 'stock/%s/price'

    class IEXRefDataEndpoint(Enum):
        """ Reference data API endpoints. """
        SYMBOLS = 'ref-data/symbols'

    ENDPOINT_FUNCTIONS = {
        IEXStockDataEndpoint.ADVANCED_STATS.name: 'get_advanced_stats',
        IEXStockDataEndpoint.CASH_FLOW.name: 'get_cash_flow',
        IEXStockDataEndpoint.PRICE.name: 'get_price',
        IEXRefDataEndpoint.SYMBOLS.name: 'get_symbols'
    }

    def __init__(self, is_prod=True):
        """ Initializes class with IEX Cloud API's base url and parameters (API token).

        :param is_prod: indicates whether to use production endpoint.
        """
        StockDataAPI.__init__(self, CONFIG['IEX_API_URL'] if is_prod else CONFIG['SANDBOX_IEX_API_URL'], is_prod)
        self.params = {'token': CONFIG['IEX_API_KEY'] if is_prod else CONFIG['SANDBOX_IEX_API_KEY']}

    def get_advanced_stats(self, symbol):
        """ Make GET request to the /stock/advanced-stats endpoint.

        :param symbol: ticker symbol for which to pull data.
        :return: dictionary containing all keys in /stock/advanced-stats.
        """
        request_url = join(self.base_url, self.IEXStockDataEndpoint.ADVANCED_STATS.value % symbol)
        return self._get_response(request_url)

    def get_cash_flow(self, symbol):
        """ Make GET request to the /stock/cash-flow endpoint.

        :param symbol: ticker symbol for which to pull data.
        :return: dictionary containing all keys in /stock/cash-flow.
        """
        request_url = join(self.base_url, self.IEXStockDataEndpoint.CASH_FLOW.value % symbol)
        return self._get_response(request_url)

    def get_price(self, symbol):
        """ Make GET request to the /stock/{symbol}/price endpoint.

        :param symbol: ticker symbol for which to pull data.
        :return: number representing most recent stock price.
        """
        request_url = join(self.base_url, self.IEXStockDataEndpoint.PRICE.value % symbol)
        return self._get_response(request_url)

    def get_symbols(self):
        """ Make GET request to the /ref-data/symbols endpoint.

        :return: dictionary containing information about all symbols supported by IEX.
        """
        request_url = join(self.base_url, self.IEXRefDataEndpoint.SYMBOLS.value)
        return self._get_response(request_url)

    def _get_response(self, request_url, params=None, headers={}, verify=True):
        """ Make GET request using the given URL, handle any errors, and return response content.

        :param request_url: URL for which to make GET request.
        :return: the response content.
        """
        response = StockDataAPI._get_response(self, request_url, params or self.params, headers, verify)
        return json.loads((response and response.content) or '{}')

    def download_symbols(self, output_name='all_iex_supported_tickers.txt'):
        """ Gets JSON representation of all symbols supported on IEX Cloud.

        :param output_name: file name in raw data directory where JSON dump should be saved.
        """

        symbol_json = self.get_symbols()
        symbols = sorted([t['symbol'] for t in filter(lambda j: j['type'] == 'cs', symbol_json)])
        save_file(RAW_DATA_DIR, output_name, '\n'.join(symbols))

    def ingest_stock_data(self, endpoints=None, symbol_json='all_iex_supported_tickers.txt', output_name='stock_data_'):
        """ Ingests financial and technical indicator data for all actively traded stocks on NASDAQ.

        :param endpoints: endpoints to hit during ingestion.
        :param symbol_json: file name in raw data directory containing IEX symbol JSON dump.
        :param output_name: base file name for partial stock data JSON dumps in processed data directory.
        """

        input_path = join(RAW_DATA_DIR, symbol_json)
        output_dir = join(PROCESSED_DATA_DIR, datetime.today().strftime('%Y%m%d') + '_partials')
        create_directory(output_dir)

        with open(input_path, 'r') as input_file:
            ingest_endpoints = endpoints or [e.value for e in self.IEXStockDataEndpoint]
            symbols = [s.strip() for s in input_file.readlines()]
            symbol_data = {}
            n = len(symbols)

            for i, symbol in enumerate(symbols):
                print('Processing symbol %s (%d of %d)' % (symbol, i + 1, n))
                args = {'symbol': symbol}
                symbol_data[symbol] = {e: getattr(self, self.ENDPOINT_FUNCTIONS[e])(**args) for e in ingest_endpoints}

                # Dump data in segments
                if (i + 1) % 10 == 0 or i == n - 1:
                    save_json(output_dir, output_name + str(i + 1) + '.json', symbol_data, True)
                    symbol_data = {}

        merge_stock_data_partials(output_dir)


def build_argument_parser():
    """ Build parser for command-line arguments.

    :return: argument parser object.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--production', action='store_true')
    parser.add_argument('-s', '--symbols', action='store_true')
    parser.add_argument('-e', '--endpoints', type=str, default='ADVANCED_STATS,CASH_FLOW,PRICE')

    return parser
