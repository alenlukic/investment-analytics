from src.analysis.trending_value import TrendingValue, TRENDING_VALUE_RANK_FACTORS
from src.utils.rank_utils import RankFactor

SUPERSTAR_RANK_FACTOR = [RankFactor('S-RANK', 4)]


class TrendingSuperstars(TrendingValue):
    """ Custom ranking methodology that extends Trending Value. """

    def __init__(self, rank_factors=TRENDING_VALUE_RANK_FACTORS, stock_data_file='stock_data_master.json'):
        """ Constructor.

        :param rank_factors: dictionary mapping rank factor names to formatted column headings.
        :param stock_data_file: JSON file containing structured stock data.
        """

        TrendingValue.__init__(self, rank_factors, stock_data_file)
        new_rank_factors = SUPERSTAR_RANK_FACTOR + [RankFactor(rf.name, rf.priority + 1) for rf in rank_factors]
        self.rank_factors = sorted(new_rank_factors)

    def rank_stocks(self):
        """ Rank the stocks. Methodology:

        1. Select the 10% most undervalued companies using the Value Composite Two indicator.
        2. Select 25 stocks with the best six-month price appreciation.
        3. TODO
        """

        TrendingValue.rank_stocks(self)

    def _create_ranking_table(self):
        """ Creates formatted table of ranked stocks. """

        TrendingValue._create_ranking_table()

        for i, row in enumerate(self.ranking_table):
            if i == 0:
                row.append('Superstar Rank')
            else:
                row.append(self.selected_stocks[i - 1].comparison_value)
