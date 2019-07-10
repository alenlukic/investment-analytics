import json
import math
from os.path import join

from src.utils.data_utils import append_if_exists, deep_get
from src.utils.math_utils import calculate_percentile, MAX_VALUE

CONFIG = json.load(open('config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.analysis.trending_value')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')

MIN_MARKET_CAP = 2 * math.pow(10, 8)


class TrendingValueStock:
    def __init__(self, symbol, stock_data):
        self.symbol = symbol
        self.stock_data = stock_data
        self.percentiles = {}
        self.rank = MAX_VALUE

    def get_price_to_book_ratio(self):
        return deep_get(self.stock_data, ['ADVANCED_STATS', 'priceToBook'])

    def get_price_to_earnings_ratio(self):
        return deep_get(self.stock_data, ['ADVANCED_STATS', 'peRatio'])

    def get_price_to_cash_flow_ratio(self):
        price = self.stock_data['PRICE']
        if price is None:
            return None
        cash_flow_array = deep_get(self.stock_data, ['CASH_FLOW', 'cashflow'])
        if cash_flow_array is None or len(cash_flow_array) == 0:
            return None
        cash_flow = cash_flow_array[0].get('cashFlow', None)

        return None if cash_flow is None else price / float(cash_flow)

    def get_price_to_sales_ratio(self):
        return deep_get(self.stock_data, ['ADVANCED_STATS', 'priceToSales'])

    def get_dividend_yield(self):
        return deep_get(self.stock_data, ['ADVANCED_STATS', 'dividendYield'])

    def get_earnings_yield(self):
        ebidta = deep_get(self.stock_data, ['ADVANCED_STATS', 'EBITDA'])
        if ebidta is None:
            return None
        ev = deep_get(self.stock_data, ['ADVANCED_STATS', 'enterpriseValue'])
        if ev is None or ev < 0:
            ev = 1

        return ebidta / float(ev)

    def set_percentiles(self, percentiles):
        self.percentiles = percentiles
        self.rank = sum(self.percentiles.values())

    def get_percentiles(self):
        return self.percentiles

    def get_rank(self):
        return self.rank

    def __eq__(self, other):
        return self.get_rank() == other.get_rank()

    def __lt__(self, other):
        return self.get_rank() < other.get_rank()


class TrendingValue:
    """ Implementation of the James O’Shaughnessy’s trending value stock ranking methodology. """

    def __init__(self, stock_data_file='stock_data_master.json'):
        self.stock_data = json.load(open(join(PROCESSED_DATA_DIR, stock_data_file), 'r'))
        self.ranked_stocks = []

        for symbol, stock_data in self.stock_data.items():
            market_cap = deep_get(stock_data, ['ADVANCED_STATS', 'marketcap'])
            if market_cap is None or market_cap < MIN_MARKET_CAP:
                continue
            self.ranked_stocks.append(TrendingValueStock(symbol, stock_data))

        self.price_to_book_ratios = []
        self.price_to_earnings_ratios = []
        self.price_to_cash_flow_ratios = []
        self.price_to_sales_ratios = []
        self.divided_yields = []
        self.earnings_yields = []

    def calculate_metrics(self):
        for stock in self.ranked_stocks:
            append_if_exists(self.price_to_book_ratios, stock.get_price_to_book_ratio())
            append_if_exists(self.price_to_earnings_ratios, stock.get_price_to_earnings_ratio())
            append_if_exists(self.price_to_cash_flow_ratios, stock.get_price_to_cash_flow_ratio())
            append_if_exists(self.price_to_sales_ratios, stock.get_price_to_sales_ratio())
            append_if_exists(self.divided_yields, stock.get_dividend_yield())
            append_if_exists(self.earnings_yields, stock.get_earnings_yield())

        self.price_to_book_ratios = sorted(self.price_to_book_ratios)
        self.price_to_earnings_ratios = sorted(self.price_to_earnings_ratios)
        self.price_to_cash_flow_ratios = sorted(self.price_to_cash_flow_ratios)
        self.price_to_sales_ratios = sorted(self.price_to_sales_ratios)
        self.divided_yields = sorted(self.divided_yields, reverse=True)
        self.earnings_yields = sorted(self.earnings_yields, reverse=True)






