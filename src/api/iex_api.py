import logging
import json
import requests
from enum import Enum
from os.path import join


CONFIG = json.load(open('../../config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.api.iex_api')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


class Endpoint(Enum):
    """ Enumeration of API endpoints used in stock data ingestion. """

    ADVANCED_STATS = '%s/advanced-stats'
    CASH_FLOW = '%s/cash-flow'
    DIVIDENDS = '%s/dividends/%s'
    EARNINGS = '%s/earnings/%s'
    FINANCIALS = '%s/financials'
    HISTORICAL_PRICES = '%s/chart/%s'
    INCOME = '%s/income'


class IEXCloudAPI:
    """ Class encapsulating the IEX Cloud API. """

    def __init__(self, api_key):
        """ Initializes class with API's base url and parameters (API token).

        Parameters:
            api_key (string): public API token needed to access the API.
        """

        self.base_url = 'https://cloud.iexapis.com/stable/stock'
        self.params = {'token': api_key}

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


def ingest_stock_data(ticker_list='all_tickers.txt', output_name='stock_data.json'):
    """ Ingests financial and technical indicator data for all actively traded stocks on NASDAQ. """

    input_path = join(PROCESSED_DATA_DIR, ticker_list)
    output_path = join(PROCESSED_DATA_DIR, output_name)

    with open(input_path, 'r') as input_file, open(output_path, 'w') as output_file:
        api = IEXCloudAPI(CONFIG['API_KEY'])
        all_tickers = [t.strip() for t in input_file.readlines()]
        all_data = {}
        n = len(all_tickers)

        for i, ticker in enumerate(all_tickers):
            print('Processing ticker %s (%d of %d)' % (ticker, i, n))
            all_data[ticker] = {
                Endpoint.ADVANCED_STATS.name: api.get_advanced_stats(ticker),
                Endpoint.CASH_FLOW.name: api.get_cash_flow(ticker),
                Endpoint.DIVIDENDS.name: api.get_dividends(ticker),
                Endpoint.EARNINGS.name: api.get_earnings(ticker),
                Endpoint.FINANCIALS.name: api.get_financials(ticker),
                Endpoint.HISTORICAL_PRICES.name: api.get_historical_prices(ticker),
                Endpoint.INCOME.name: api.get_income(ticker)
            }

        json.dump(all_data, output_file, indent=2, sort_keys=True)


if __name__ == '__main__':
    ingest_stock_data()
