import logging
import json
from os import listdir
from os.path import basename, join


CONFIG = json.load(open('config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.utils.data_utils')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


def merge_stock_data(input_dir, output_suffix='_stock_data.json'):
    """ Uses raw dump from NASDAQ's FTP server to generate a list containing all tickers traded on the exchange.

    Parameters:
        input_dir (str): directory containing partial stock data dumps
        output_suffix (str): suffix of output file name (will be saved to processed data directory)
    """
    partial_files = [f for f in filter(lambda j: j.endswith('.json'), listdir(input_dir))]
    merged_data = {}

    for pf in partial_files:
        partial_json = json.load(open(join(input_dir, pf), 'r'))
        merged_data.update(partial_json)

    prefix = basename(input_dir)
    with open(join(PROCESSED_DATA_DIR, prefix + output_suffix), 'w') as w:
        json.dump(merged_data, w, sort_keys=True)
