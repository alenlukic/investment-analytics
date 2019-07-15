from src.analysis.strategy import STOCK_INFO_FACTORS
from src.analysis.trending_value import TrendingValue, TRENDING_VALUE_RANK_FACTORS, VALUE_FACTORS
from src.utils.rank_utils import RankFactor


SUPERSTAR_RANK_FACTOR = [RankFactor('S-RANK', 4, lambda x: str(x))]


class TrendingSuperstars(TrendingValue):
    """ Custom ranking methodology that extends Trending Value. """

    def __init__(self, rank_factors=TRENDING_VALUE_RANK_FACTORS, stock_data_file='stock_data_master.json'):
        """ Constructor.

        :param rank_factors: dictionary mapping rank factor names to formatted column headings.
        :param stock_data_file: JSON file containing structured stock data.
        """

        TrendingValue.__init__(self, rank_factors, stock_data_file)
        updated_tv_factors = [rf.init(rf.priority + 1) for rf in rank_factors]
        self.rank_factors = sorted(STOCK_INFO_FACTORS + SUPERSTAR_RANK_FACTOR + updated_tv_factors)

    def rank_stocks(self):
        """ Rank the stocks. Methodology:

        1. Select the 10% most undervalued companies using the Value Composite Two indicator.
        2. Select 100 stocks with best six-month price appreciation.
        3. Rank stocks by 'Superstar Rank,' which is defined as the cardinality of the stock's value factors in their
        top respective decile.
        4. Filter out any stocks with a Superstar Rank of 0.
        """

        TrendingValue.rank_stocks(self)

        top_stocks = self.selected_stocks[0:min(len(self.selected_stocks), 100)]

        for stock in top_stocks:
            rank_factors = stock.get_rank_factors()
            superstar_rank = sum([1 if rank_factors[vf.name] <= 10 else 0 for vf in VALUE_FACTORS])
            stock.update_rank_factors({'S-RANK': superstar_rank})
            stock.set_comparison_value(superstar_rank)

        self.selected_stocks = sorted(filter(lambda s: s.get_rank_factors()['S-RANK'] > 0, top_stocks), reverse=True)
        self._set_ranks()


if __name__ == '__main__':
    ranker = TrendingSuperstars()
    ranker.rank_stocks()
    ranker.create_ranking_table()
    ranker.print_ranking()
    ranker.save_ranking('trending_superstars_')
