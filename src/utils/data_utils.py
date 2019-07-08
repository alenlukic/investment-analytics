import logging
import json
import requests
from os.path import join

CONFIG = json.load(open('../../config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.utils.data_utils')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')
RAW_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'raw')

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


def create_ticker_list(output_name='all_tickers.txt'):
    """ Uses raw dump from NASDAQ's FTP server to generate a list containing all tickers traded on the exchange.

    Parameters:
        output_name (string): output file name - will be located in the processed data directory
    """

    response = requests.get('http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt')
    traded_companies = response.text.split('\r\n')
    tickers = set()
    errors = []

    for row in traded_companies:
        try:
            segments = row.split('|')
            ticker = segments[1]
            tickers.add(ticker.split('$')[0])
        except Exception as e:
            errors.append((row, str(e)))
            continue

    for row, error in errors:
        logging.warning('The following error occurred while processing row %s: %s', row, error)

    output_path = join(PROCESSED_DATA_DIR, output_name)
    with open(output_path, 'w') as output_file:
        sorted_tickers = sorted(list(tickers))
        output_file.write('\n'.join(sorted_tickers))
