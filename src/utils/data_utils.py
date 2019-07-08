import logging
import json
from os.path import join

CONFIG = json.load(open('../../config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.utils.data_utils')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')
RAW_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'raw')

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


def create_stock_list(input_name='nasdaq_stock_dump.txt', output_name='all_tickers.txt'):
    """ Uses raw dump from NASDAQ's FTP server to generate a list containing all tickers traded on the exchange.

    Parameters:
        input_name (string): raw dump file name, located in the raw data directory
        output_name (string): output file name - will be located in the processed data directory
    """

    input_path = join(RAW_DATA_DIR, input_name)
    output_path = join(PROCESSED_DATA_DIR, output_name)

    with open(input_path, 'r') as input_file, open(output_path, 'w') as output_file:
        input_lines = [r.strip() for r in input_file.readlines()]
        tickers = set()
        errors = []

        for row in input_lines:
            try:
                segments = row.split('|')
                ticker = segments[1]
                tickers.add(ticker.split('$')[0])
            except Exception as e:
                errors.append((row, str(e)))
                continue

        for row, error in errors:
            logging.warning('The following error occurred while processing row %s: %s', row, error)

        sorted_tickers = sorted(list(tickers))
        output_file.write('\n'.join(sorted_tickers))
