import logging
import requests
from datetime import datetime

from src.definitions.config import *
from src.definitions.routes import *
from src.utils.data_utils import merge_stock_data_partials
from src.utils.file_utils import create_directory, load_stock_symbols, save_file, save_json


logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


class StockDataAPI:
    """ Base class for any API used to obtain stock data. """

    def __init__(self, base_url, is_prod=True):
        self.base_url = base_url
        self.is_prod = is_prod

    def _get_response(self, request_url, params={}, headers={}, verify=True):
        # Make GET request using the given URL, handle any errors, and return response
        try:
            response = requests.get(request_url, params=params, headers=headers, verify=verify)
            if response.status_code == 200:
                return response
            response_context = self._error_response_context(response)
            logging.warning('Got error code response from %s: %s', request_url, json.dumps(response_context))
            return None
        except Exception as e:
            logging.warning('The following exception occurred trying to make request to %s: %s', request_url, str(e))
            return None

    def _error_response_context(self, response):
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

    ENDPOINT_FUNCTIONS = {
        FinancialContentEndpoint.DETAILED_QUOTE.name: 'quote/detailedquote',
        FinancialContentEndpoint.HISTORICAL_DATA.name: 'action/gethistoricaldata',
    }

    def __init__(self):
        StockDataAPI.__init__(self, CONFIG['FINANCIAL_CONTENT_API_URL'])

    def get_detailed_quote(self, symbol):
        params = {'Symbol': 'NY:' + symbol}
        endpoint = FinancialContentEndpoint.DETAILED_QUOTE.value
        referer_url = self._generate_referer_url(endpoint, params)
        headers = {'Upgrade-Insecure-Requests': '1', 'Referer': referer_url}

        return self._get_response(join(self.base_url, endpoint), params, headers)

    def get_historical_data(self, symbol, year, month, num_months=12):
        params = {'Symbol': 'NY:' + symbol, 'Year': year, 'Month': month, 'Range': num_months}
        endpoint = FinancialContentEndpoint.HISTORICAL_DATA.value
        referer_url = self._generate_referer_url(endpoint, params)
        headers = {'Upgrade-Insecure-Requests': '1', 'Referer': referer_url}

        return self._get_response(join(self.base_url, endpoint), params, headers)

    def _generate_referer_url(self, endpoint, params):
        # Generates referer URL needed to make request to FC
        param_str = '?' + '&'.join([(k + '=' + v).replace(':', '%3A') for k, v in params.items()])
        return join(self.base_url, endpoint + param_str)

    def _get_response(self, request_url, params={}, headers={}, verify=False):
        response = StockDataAPI._get_response(self, request_url, params, headers, verify)
        return (response and response.text) or ''


class IEXCloudAPI(StockDataAPI):
    """ Class encapsulating IEX Cloud API. """

    ENDPOINT_FUNCTIONS = {
        IEXStockDataEndpoint.ADVANCED_STATS.name: 'get_advanced_stats',
        IEXStockDataEndpoint.CASH_FLOW.name: 'get_cash_flow',
        IEXStockDataEndpoint.KEY_STATS.name: 'get_key_stats',
        IEXStockDataEndpoint.PRICE.name: 'get_price',
        IEXRefDataEndpoint.SYMBOLS.name: 'get_symbols'
    }

    def __init__(self, is_prod=True):
        StockDataAPI.__init__(self, CONFIG['IEX_API_URL'] if is_prod else CONFIG['SANDBOX_IEX_API_URL'], is_prod)
        self.params = {'token': CONFIG['IEX_API_KEY'] if is_prod else CONFIG['SANDBOX_IEX_API_KEY']}

    def get_advanced_stats(self, symbol):
        request_url = join(self.base_url, IEXStockDataEndpoint.ADVANCED_STATS.value % symbol)
        return self._get_response(request_url)

    def get_cash_flow(self, symbol):
        request_url = join(self.base_url, IEXStockDataEndpoint.CASH_FLOW.value % symbol)
        return self._get_response(request_url)

    def get_key_stats(self, symbol):
        request_url = join(self.base_url, IEXStockDataEndpoint.KEY_STATS.value % symbol)
        return self._get_response(request_url)

    def get_price(self, symbol):
        request_url = join(self.base_url, IEXStockDataEndpoint.PRICE.value % symbol)
        return self._get_response(request_url)

    def get_symbols(self):
        request_url = join(self.base_url, IEXRefDataEndpoint.SYMBOLS.value)
        return self._get_response(request_url)

    def _get_response(self, request_url, params=None, headers={}, verify=True):
        response = StockDataAPI._get_response(self, request_url, params or self.params, headers, verify)
        return json.loads((response and response.content) or '{}')

    def download_symbols(self, output_name=TICKER_SYMBOLS):
        symbol_json = self.get_symbols()
        symbols = sorted([t['symbol'] for t in filter(lambda j: j['type'] == 'cs', symbol_json)])
        save_file(RAW_DATA_DIR, output_name, '\n'.join(symbols))

    def update_stock_data(self, symbols=None, endpoints=None, output_name='stock_data_'):
        # TODO: output to DB
        output_dir = join(PROCESSED_DATA_DIR, datetime.today().strftime('%Y%m%d') + '_partials')
        create_directory(output_dir)

        symbol_queue = symbols or load_stock_symbols()
        ingest_endpoints = endpoints or [e.value for e in IEXStockDataEndpoint]
        symbol_data = {}
        n = len(symbol_queue)

        for i, symbol in enumerate(symbol_queue):
            print('Processing symbol %s (%d of %d)' % (symbol, i + 1, n))

            args = {'symbol': symbol}
            symbol_data[symbol] = {e: getattr(self, self.ENDPOINT_FUNCTIONS[e])(**args) for e in ingest_endpoints}

            # Dump data in segments
            if (i + 1) % 10 == 0 or i == n - 1:
                print(str(symbol_data))

                save_json(output_dir, output_name + str(i + 1) + '.json', symbol_data, True)
                symbol_data = {}

        merge_stock_data_partials(output_dir)
