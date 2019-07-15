import json
import math
from copy import deepcopy
from os.path import join

from src.analysis.stock import RankedStock
from src.analysis.strategy import Strategy
from src.utils.data_utils import append_if_exists, deep_get, merge_dictionaries, pad_with_median
from src.utils.math_utils import calculate_percentile
from src.utils.rank_utils import RankFactor


CONFIG = json.load(open('config.json', 'r'))
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')

MIN_MARKET_CAP = 2 * math.pow(10, 8)
MOMENTUM_FACTOR = [RankFactor('6M P/P', 4)]
VALUE_FACTORS = [
    RankFactor('P/B', 5),
    RankFactor('P/E', 6),
    RankFactor('P/CF', 7),
    RankFactor('P/S', 8),
    RankFactor('DY%', 9),
    RankFactor('EY%', 10)
]
TRENDING_VALUE_RANK_FACTORS = MOMENTUM_FACTOR + VALUE_FACTORS


class TrendingValue(Strategy):
    """ Implementation of the James O’Shaughnessy’s trending value stock ranking methodology. """

    def __init__(self, rank_factors=TRENDING_VALUE_RANK_FACTORS, stock_data_file='stock_data_master.json'):
        """ Constructor.

        :param rank_factors: dictionary mapping rank factor names to formatted column headings.
        :param stock_data_file: JSON file containing structured stock data.
        """

        Strategy.__init__(self, rank_factors, stock_data_file)

    def rank_stocks(self):
        """ Rank the stocks. Methodology:

        1. Select the 10% most undervalued companies using the Value Composite Two indicator.
        2. Select 25 stocks with the best six-month price appreciation.
        """

        self._calculate_metrics()

        # Select top 10% of stocks based on intermediate ranking
        decile = int(self.num_stocks * 0.1)
        top_decile = deepcopy(sorted(self.stocks)[0:decile])

        # Set six-month price appreciation as new comparison metric
        for stock in top_decile:
            stock.set_comparison_metrics({'6M P/P': stock.six_month_percent_delta()})

        # Re-rank top decile
        self.selected_stocks = sorted(top_decile, reverse=True)
        self._set_ranks()

    def _calculate_metrics(self):
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

        # Sort each metric in order of descending goodness
        n = self.num_stocks
        price_to_book_ratios = sorted(pad_with_median(price_to_book_ratios, n))
        price_to_earnings_ratios = sorted(pad_with_median(price_to_earnings_ratios, n))
        price_to_cash_flow_ratios = sorted(pad_with_median(price_to_cash_flow_ratios, n))
        price_to_sales_ratios = sorted(pad_with_median(price_to_sales_ratios, n))
        divided_yields = sorted(pad_with_median(divided_yields, n), reverse=True)
        earnings_yields = sorted(pad_with_median(earnings_yields, n), reverse=True)

        # Generate ranking factors for each stock
        for stock in self.stocks:
            info_factors = {
                'Company Name': stock.get_company_name(),
                'Symbol': stock.get_symbol(),
                'Price': stock.price()
            }
            momentum_factor = {'6M P/P': stock.six_month_percent_delta()}
            value_factors = {
                'P/B': calculate_percentile(stock.price_to_book_ratio(), price_to_book_ratios, n),
                'P/E': calculate_percentile(stock.price_to_earnings_ratio(), price_to_earnings_ratios, n),
                'P/CF': calculate_percentile(stock.price_to_cash_flow_ratio(), price_to_cash_flow_ratios, n),
                'P/S': calculate_percentile(stock.price_to_sales_ratio(), price_to_sales_ratios, n),
                'DY%': calculate_percentile(stock.dividend_yield(), divided_yields, n),
                'EY%': calculate_percentile(stock.earnings_yield(), earnings_yields, n),
            }

            rank_factors = merge_dictionaries([info_factors, momentum_factor, value_factors])
            stock.set_rank_factors(rank_factors)
            stock.set_comparison_metrics(value_factors)

    def _initialize_stocks(self):
        """ Initializes set of stocks by filtering out any companies with a market cap under $200M. """

        stocks = []
        for symbol, stock_data in self.stock_data.items():
            market_cap = deep_get(stock_data, ['ADVANCED_STATS', 'marketcap'])
            if market_cap is None or market_cap < MIN_MARKET_CAP:
                continue
            stocks.append(RankedStock(symbol, stock_data))

        return stocks


if __name__ == '__main__':
    ranker = TrendingValue()
    ranker.rank_stocks()
    ranker.create_ranking_table()
    ranker.print_ranking()
