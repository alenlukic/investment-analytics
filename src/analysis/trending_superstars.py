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
        column_headings = SUPERSTAR_RANK_FACTOR + [RankFactor(rf.name, rf.priority + 1) for rf in rank_factors]
        self.column_headings = sorted(column_headings)

    def rank_stocks(self):
        """ Rank the stocks. Methodology:

        1. Select the 10% most undervalued companies using the Value Composite Two indicator.
        2. Select 25 stocks with the best six-month price appreciation.
        3. TODO
        """

        TrendingValue.rank_stocks(self)

        for stock in self.selected_stocks:
            stock_rank_factors = stock.get_rank_factors()
            comparison_value = [1 if stock_rank_factors[f] <= 10 else 0 for f in filter(lambda x:
                                                                                        x != 'month6ChangePercent', self.rank_factors.values())]
            stock.set_comparison_value(comparison_value)

        self.selected_stocks = sorted(self.selected_stocks, reverse=True)
        self._create_ranking_table()

    def _create_ranking_table(self):
        """ Creates formatted table of ranked stocks. """

        TrendingValue._create_ranking_table()

        for i, row in enumerate(self.ranking_table):
            if i == 0:
                row.append('Superstar Rank')
            else:
                row.append(self.selected_stocks[i - 1].comparison_value)
