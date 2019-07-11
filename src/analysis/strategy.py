import json
from os.path import join

from src.analysis.stock import RankedStock

CONFIG = json.load(open('config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.analysis.trending_value')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')


class Strategy:
    """ Base class for an investment strategy. """

    def __init__(self, stock_data_file='stock_data_master.json'):
        self.stock_data = json.load(open(join(PROCESSED_DATA_DIR, stock_data_file), 'r'))
        self.stocks = self.initialize_stocks()

    def initialize_stocks(self):
        return [RankedStock(symbol, stock_data) for symbol, stock_data in self.stock_data.items()]

    def rank_stocks(self):
        self.stocks = sorted(self.stocks)

    # TODO
    def print_ranking(self):
        return
