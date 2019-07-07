import logging
from os.path import join

LOG_FILE = '../../logs/src.utils.data_utils'
PROCESSED_DATA_DIR = '../../data/processed'
RAW_DATA_DIR = '../../data/raw'

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


""" Uses raw dump from NASDAQ's FTP server to generate a list containing all tickers traded on the exchange.

Parameters:
input_name (string): raw dump file name, located in the raw data directory
output_name (string): output file name - will be located in the processed data directory

"""


def create_stock_list(input_name='nasdaq_stock_dump.txt', output_name='all_tickers.txt'):
    input_path = join(RAW_DATA_DIR, input_name)
    output_path = join(RAW_DATA_DIR, output_name)

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

        output_file.write('\n'.join(tickers))

