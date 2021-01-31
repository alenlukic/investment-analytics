import json
from os.path import join

CONFIG = json.load(open('config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.api.iex_api')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')
RAW_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'raw')
TICKER_TARGET = CONFIG['TICKER_TARGET']
