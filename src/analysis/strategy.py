import json
from datetime import datetime
from os.path import join
from tabulate import tabulate

from src.analysis.stock import RankedStock
from src.utils.file_utils import save_file, save_json
from src.utils.formatting_utils import format_currency, format_decimal, format_rank
from src.utils.math_utils import MAX_VALUE

CONFIG = json.load(open('config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.analysis.trending_value')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')


class Strategy:
    """ Base class for an investment strategy. """

    def __init__(self, rank_factors, stock_data_file='stock_data_master.json'):
        """ Constructor.

        :param rank_factors: dictionary mapping formatted column headings to rank factor names.
        :param stock_data_file: JSON file containing structured stock data.
        """

        self.stock_data = json.load(open(join(PROCESSED_DATA_DIR, stock_data_file), 'r'))
        self.stocks = self._initialize_stocks()
        self.num_stocks = len(self.stocks)
        self.rank_factors = rank_factors
        self.column_headings = sorted(rank_factors.keys())

        # Set after ranking
        self.selected_stocks = []
        self.ranking_table = []

    def rank_stocks(self):
        """ Rank the stocks. """

        self.selected_stocks = sorted(self.stocks)
        self.ranking_table = self._create_ranking_table()

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

        save_file(output_dir, ranking_file_prefix + '.txt', tabulate(self.ranking_table))
        save_json(output_dir, ranking_file_prefix + '.json', {'ranking': self.ranking_table})

    def _create_ranking_table(self):
        """ Creates formatted table of ranked stocks. """

        table = [['Rank', 'Company Name', 'Symbol', 'Price'] + self.column_headings]

        for i, stock in enumerate(self.selected_stocks):
            row = [format_rank(i + 1), stock.get_company_name(), stock.get_symbol(), format_currency(stock.price())]
            stock_rank_factors = stock.get_rank_factors()

            for heading in self.column_headings:
                stock_metric_value = stock_rank_factors[self.rank_factors[heading]]
                row.append(format_decimal(stock_metric_value))

            table.append(row)

        return table

    def _initialize_stocks(self):
        """ Initialize set of stocks to analyze. """
        return [RankedStock(symbol, stock_data) for symbol, stock_data in self.stock_data.items()]
