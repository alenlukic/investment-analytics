import json
from datetime import datetime
from os.path import join
from tabulate import tabulate

from src.analysis.stock import RankedStock
from src.utils.file_utils import save_file, save_json
from src.utils.formatting_utils import format_currency, format_rank
from src.utils.math_utils import MAX_VALUE
from src.utils.rank_utils import RankFactor


CONFIG = json.load(open('config.json', 'r'))
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')

STOCK_INFO_FACTORS = [
    RankFactor('Rank', 0, format_rank),
    RankFactor('Company Name', 1, lambda x: x),
    RankFactor('Symbol', 2, lambda x: x),
    RankFactor('Price', 3, format_currency)
]


class Strategy:
    """ Base class for an investment strategy. """

    def __init__(self, rank_factors, stock_data_file='stock_data_master.json'):
        """ Constructor.

        :param rank_factors: list of ranking factors to include in output ranking in addition to STOCK_INFO_FACTORS.
        :param stock_data_file: JSON file containing structured stock data.
        """

        self.stock_data = json.load(open(join(PROCESSED_DATA_DIR, stock_data_file), 'r'))
        self.stocks = self._initialize_stocks()
        self.num_stocks = len(self.stocks)
        self.rank_factors = sorted(STOCK_INFO_FACTORS + rank_factors)

        # Set after ranking
        self.ranked_stocks = []
        self.ranking_table = []

    def rank_stocks(self):
        """ Rank the stocks. """

        self.ranked_stocks = sorted(self.stocks)
        self._set_ranks()

    def create_ranking_table(self):
        """ Creates formatted table of ranked stocks. """

        table = [[c.name for c in self.rank_factors]]

        for stock in self.ranked_stocks:
            row = []
            stock_rank_factors = stock.get_rank_factors()

            for factor in self.rank_factors:
                stock_metric_value = stock_rank_factors[factor.name]
                format_function = factor.get_format_function()
                row.append(format_function(stock_metric_value))

            table.append(row)

        self.ranking_table = table

    def print_ranking(self, num=None):
        """ Prints formatted ranking table.

        :param num: (optional) number of stocks to print (defaults to all).
        """

        n = min(len(self.ranking_table), (num or MAX_VALUE) + 1)
        print(tabulate(self.ranking_table[0:n]))

    def save_ranking(self, file_prefix):
        """ Saves formatted stock ranking to disk.

        :param file_prefix: file name prefix.
        """

        ranking_file_prefix = file_prefix + datetime.today().strftime('%Y%m%d')
        output_dir = join(PROCESSED_DATA_DIR, 'stock_rankings')

        table_ranking = tabulate(self.ranking_table)
        save_file(output_dir, ranking_file_prefix + '.txt', table_ranking)
        json_ranking = {s.get_symbol(): s.get_rank_factors() for s in self.ranked_stocks}
        save_json(output_dir, ranking_file_prefix + '.json', json_ranking)

    def get_ranked_stocks(self):
        """ Returns ranked stocks. """
        return self.ranked_stocks

    def _initialize_stocks(self):
        """ Initialize set of stocks to analyze. """
        return [RankedStock(symbol, stock_data) for symbol, stock_data in self.stock_data.items()]

    def _set_ranks(self):
        """ Set the Rank column on newly ranked stocks. """
        for i, stock in enumerate(self.ranked_stocks):
            stock.update_rank_factors({'Rank': i + 1})
