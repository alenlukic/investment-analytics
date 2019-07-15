import json
import math
from copy import deepcopy
from os.path import join

from src.analysis.stock import RankedStock
from src.analysis.strategy import Strategy
from src.utils.data_utils import append_if_exists, deep_get, pad_with_median
from src.utils.math_utils import calculate_percentile


CONFIG = json.load(open('config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.analysis.trending_value')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')

MIN_MARKET_CAP = 2 * math.pow(10, 8)
TRENDING_VALUE_RANK_FACTORS = {
    'P/B': 'priceToBook',
    'P/E': 'peRatio',
    'P/CF': 'priceToCashFlow',
    'P/S': 'priceToSales',
    'DY%': 'dividendYield',
    'EY%': 'earningsYield',
    '6M P/P': 'month6ChangePercent'
}


class TrendingValue(Strategy):
    """ Implementation of the James O’Shaughnessy’s trending value stock ranking methodology. """

    def __init__(self, rank_factors=TRENDING_VALUE_RANK_FACTORS, stock_data_file='stock_data_master.json'):
        """
        Constructor.

        :param rank_factors: dictionary mapping rank factor names to formatted column headings.
        :param stock_data_file: JSON file containing structured stock data.
        """

        Strategy.__init__(self, rank_factors, stock_data_file)

    def calculate_metrics(self):
        """ Calculate value metric percentiles and momentum factor (6-month price % delta). """

        price_to_book_ratios = []
        price_to_earnings_ratios = []
        price_to_cash_flow_ratios = []
        price_to_sales_ratios = []
        divided_yields = []
        earnings_yields = []

        # Get metrics for each stock
        for stock in self.stocks:
            append_if_exists(price_to_book_ratios, stock.price_to_book_ratio())
            append_if_exists(price_to_earnings_ratios, stock.price_to_earnings_ratio())
            append_if_exists(price_to_cash_flow_ratios, stock.price_to_cash_flow_ratio())
            append_if_exists(price_to_sales_ratios, stock.price_to_sales_ratio())
            append_if_exists(divided_yields, stock.dividend_yield())
            append_if_exists(earnings_yields, stock.earnings_yield())

        # Sort each metric in order of descending "goodness"
        n = self.num_stocks
        price_to_book_ratios = sorted(pad_with_median(price_to_book_ratios, n))
        price_to_earnings_ratios = sorted(pad_with_median(price_to_earnings_ratios, n))
        price_to_cash_flow_ratios = sorted(pad_with_median(price_to_cash_flow_ratios, n))
        price_to_sales_ratios = sorted(pad_with_median(price_to_sales_ratios, n))
        divided_yields = sorted(pad_with_median(divided_yields, n), reverse=True)
        earnings_yields = sorted(pad_with_median(earnings_yields, n), reverse=True)

        # Generate metric percentiles for each stock
        for stock in self.stocks:
            rank_factors = {
                'priceToBook': calculate_percentile(stock.price_to_book_ratio(), price_to_book_ratios, n),
                'peRatio': calculate_percentile(stock.price_to_earnings_ratio(), price_to_earnings_ratios, n),
                'priceToCashFlow': calculate_percentile(stock.price_to_cash_flow_ratio(), price_to_cash_flow_ratios, n),
                'priceToSales': calculate_percentile(stock.price_to_sales_ratio(), price_to_sales_ratios, n),
                'dividendYield': calculate_percentile(stock.dividend_yield(), divided_yields, n),
                'earningsYield': calculate_percentile(stock.earnings_yield(), earnings_yields, n),
                'month6ChangePercent': stock.six_month_percent_delta()
            }
            stock.set_rank_factors(rank_factors)

            comparison_metrics = deepcopy(rank_factors)
            del comparison_metrics['month6ChangePercent']
            stock.set_comparison_metrics(comparison_metrics)

    def rank_stocks(self):
        """
        Rank the stocks. Methodology:

        1. Select the 10% most undervalued companies using the Value Composite Two indicator.
        2. Select 25 stocks with the best six-month price appreciation.
        """

        # Select top 10% of stocks based on intermediate ranking
        decile = int(self.num_stocks * 0.1)
        top_decile = deepcopy(sorted(self.stocks)[0:decile])

        # Set six-month price appreciation as new comparison metric
        for stock in top_decile:
            stock.set_comparison_metrics({'month6ChangePercent': stock.six_month_percent_delta()})

        # Re-rank top decile
        self.selected_stocks = sorted(top_decile, reverse=True)
        self._format_ranking()

    def save_ranking(self, file_prefix='trending_value_'):
        """
        Saves formatted stock ranking to disk.

        :param file_prefix: file name prefix.
        """
        Strategy.save_ranking(self, file_prefix)

    def _initialize_stocks(self):
        stocks = []

        for symbol, stock_data in self.stock_data.items():
            market_cap = deep_get(stock_data, ['ADVANCED_STATS', 'marketcap'])
            if market_cap is None or market_cap < MIN_MARKET_CAP:
                continue
            stocks.append(RankedStock(symbol, stock_data))

        return stocks


if __name__ == '__main__':
    tvs = TrendingValue()
    tvs.calculate_metrics()
    tvs.rank_stocks()
    tvs.print_ranking()
    tvs.save_ranking()
