import json
from datetime import datetime
from os.path import join
from tabulate import tabulate

from src.analysis.stock import RankedStock
from src.utils.formatting_utils import format_decimal, format_rank

CONFIG = json.load(open('config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.analysis.trending_value')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')


class Strategy:
    """ Base class for an investment strategy. """

    def __init__(self, rank_factors, stock_data_file='stock_data_master.json'):
        """
        Constructor.

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
        self.formatted_ranking = ''

    def rank_stocks(self):
        """ Rank the stocks. """

        self.selected_stocks = sorted(self.stocks)
        self._format_ranking()

    def print_ranking(self):
        """ Prints formatted ranking table. """
        print(self.formatted_ranking)

    def save_ranking(self, file_prefix):
        """
        Saves formatted stock ranking to disk.

        :param file_prefix: file name prefix.
        """

        ranking_file_name = file_prefix + datetime.today().strftime('%Y%m%d') + '.txt'
        output_path = join(PROCESSED_DATA_DIR, 'stock_rankings', ranking_file_name)
        with open(output_path, 'w') as w:
            w.write(self.formatted_ranking)

    def _format_ranking(self):
        """ Creates formatted table of ranked stocks. """

        table = [['Rank', 'Company Name', 'Symbol', 'Price'] + self.column_headings]

        for i, stock in enumerate(self.selected_stocks):
            row = [format_rank(i + 1), stock.get_company_name(), stock.get_symbol(), format_decimal(stock.price(), 2)]
            stock_rank_factors = stock.get_rank_factors()

            for heading in self.column_headings:
                stock_metric_value = stock_rank_factors[self.rank_factors[heading]]
                row.append(format_decimal(stock_metric_value))

            table.append(row)

        self.formatted_ranking = tabulate(table)

    def _initialize_stocks(self):
        """ Initialize set of stocks to analyze. """
        return [RankedStock(symbol, stock_data) for symbol, stock_data in self.stock_data.items()]
