import json
import math
from os.path import join

from src.analysis.stock import RankedStock
from src.analysis.strategy import Strategy
from src.utils.data_utils import append_if_exists, deep_get
from src.utils.math_utils import calculate_percentile

CONFIG = json.load(open('config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.analysis.trending_value')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')

MIN_MARKET_CAP = 2 * math.pow(10, 8)


class TrendingValueStock(RankedStock):
    """ Stock ranked by the Trending Value strategy. """

    def __init__(self, symbol, stock_data):
        """ Class constructor. """

        RankedStock.__init__(self, symbol, stock_data)
        self.percentiles = {}

    def set_percentiles(self, percentiles):
        """ Set the dictionary of metric percentiles (and also set the rank as the sum of these percentiles).

        :param percentiles: dictionary mapping metrics to percentiles relative to the population of stocks.
        """

        self.percentiles = percentiles
        self.set_rank(sum(self.percentiles.values()))

    def get_percentiles(self):
        """ :returns: The metric percentile dictionary. """
        return self.percentiles


class TrendingValue(Strategy):
    """ Implementation of the James O’Shaughnessy’s trending value stock ranking methodology. """

    def __init__(self, stock_data_file='stock_data_master.json'):
        Strategy.__init__(self, stock_data_file)
        self.price_to_book_ratios = []
        self.price_to_earnings_ratios = []
        self.price_to_cash_flow_ratios = []
        self.price_to_sales_ratios = []
        self.divided_yields = []
        self.earnings_yields = []

    def initialize_stocks(self):
        stocks = []

        for symbol, stock_data in self.stock_data.items():
            market_cap = deep_get(stock_data, ['ADVANCED_STATS', 'marketcap'])
            if market_cap is None or market_cap < MIN_MARKET_CAP:
                continue
            stocks.append(TrendingValueStock(symbol, stock_data))

        return stocks

    def calculate_metrics(self):
        # Get metrics for each stock
        for stock in self.ranked_stocks:
            append_if_exists(self.price_to_book_ratios, stock.get_price_to_book_ratio())
            append_if_exists(self.price_to_earnings_ratios, stock.get_price_to_earnings_ratio())
            append_if_exists(self.price_to_cash_flow_ratios, stock.get_price_to_cash_flow_ratio())
            append_if_exists(self.price_to_sales_ratios, stock.get_price_to_sales_ratio())
            append_if_exists(self.divided_yields, stock.get_dividend_yield())
            append_if_exists(self.earnings_yields, stock.get_earnings_yield())

        # Sort each metric in order of descending "goodness"
        self.price_to_book_ratios = sorted(self.price_to_book_ratios)
        self.price_to_earnings_ratios = sorted(self.price_to_earnings_ratios)
        self.price_to_cash_flow_ratios = sorted(self.price_to_cash_flow_ratios)
        self.price_to_sales_ratios = sorted(self.price_to_sales_ratios)
        self.divided_yields = sorted(self.divided_yields, reverse=True)
        self.earnings_yields = sorted(self.earnings_yields, reverse=True)

        # Generate metric percentiles for each stock
