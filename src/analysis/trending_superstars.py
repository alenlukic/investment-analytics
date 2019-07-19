from src.analysis.strategy import STOCK_INFO_FACTORS
from src.analysis.trending_value import TrendingValue, TRENDING_VALUE_RANK_FACTORS, VALUE_FACTORS
from src.utils.data_utils import append_if_exists, pad_with_median
from src.utils.math_utils import calculate_percentile
from src.utils.rank_utils import RankFactor


SUPERSTAR_MOMENTUM_FACTOR = [RankFactor('S-M FACTOR', 4)]


class TrendingSuperstars(TrendingValue):
    """ Custom ranking methodology that extends Trending Value. """

    def __init__(self, rank_factors=TRENDING_VALUE_RANK_FACTORS, stock_data_file='stock_data_master.json'):
        """ Constructor.

        :param rank_factors: dictionary mapping rank factor names to formatted column headings.
        :param stock_data_file: JSON file containing structured stock data.
        """

        TrendingValue.__init__(self, rank_factors, stock_data_file)
        updated_tv_factors = [rf.init(rf.priority + 1) for rf in rank_factors]
        self.rank_factors = sorted(STOCK_INFO_FACTORS + SUPERSTAR_MOMENTUM_FACTOR + updated_tv_factors)

    def rank_stocks(self, superstar_weight=0.4, momentum_weight=0.6):
        """ Rank the stocks. Methodology:

        1. Select the 10% most undervalued companies using the Value Composite Two indicator.
        2. Calculate 'Superstar Rank' for each stock, which is defined as: cardinality(stock value factors in top 90th
        percentile).
        3. Rank stocks using a weighted combination of Superstar Rank and price momentum percentiles.

        :param superstar_weight: weighting to use for Superstar Rank percentile.
        :param momentum_weight: weighting to use for price momentum percentile.
        """

        # First apply VC2 strategy
        TrendingValue.rank_stocks(self)

        # Calculate Superstar Rank for each stock
        superstar_ranks = []
        momentum_factors = []

        for stock in self.selected_stocks:
            rank_factors = stock.get_rank_factors()
            superstar_rank = sum([1 if rank_factors[vf.name] <= 10 else 0 for vf in VALUE_FACTORS])
            stock.update_rank_factors({'S-M FACTOR': superstar_rank})
            append_if_exists(superstar_ranks, superstar_rank)
            append_if_exists(momentum_factors, stock.six_month_percent_delta())

        # Calculate percentiles and set S-M (superstar-momentum) factor
        n = len(self.selected_stocks)
        superstar_ranks = sorted(pad_with_median(superstar_ranks, n), reverse=True)
        momentum_factors = sorted(pad_with_median(momentum_factors, n), reverse=True)

        for stock in self.selected_stocks:
            superstar_percentile = calculate_percentile(stock.get_rank_factors()['S-M FACTOR'], superstar_ranks, n)
            momentum_percentile = calculate_percentile(stock.six_month_percent_delta(), momentum_factors, n)
            superstar_momentum = (superstar_weight * superstar_percentile) + (momentum_weight * momentum_percentile)
            stock.update_rank_factors({'S-M FACTOR': superstar_momentum})
            stock.set_comparison_value(superstar_momentum)

        self.selected_stocks = sorted(self.selected_stocks)
        self._set_ranks()


if __name__ == '__main__':
    ranker = TrendingSuperstars()
    ranker.rank_stocks()
    ranker.create_ranking_table()
    ranker.print_ranking()
    ranker.save_ranking('trending_superstars_')
