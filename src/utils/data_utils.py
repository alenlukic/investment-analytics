import logging
import json
from os import listdir
from os.path import basename, join
from statistics import median

from src.utils.file_utils import save_json


CONFIG = json.load(open('config.json', 'r'))
LOG_FILE = join(CONFIG['LOG_DIRECTORY'], 'src.utils.data_utils')
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


def append_if_exists(target_list, value):
    """ Appends value to the list if it's not None.

    :param target_list: list to append value to.
    :param value: the potential value.
    """

    if value is not None:
        target_list.append(value)


def deep_get(nested_object, path):
    """ Gets deeply nested value from object.

    :param nested_object: Deeply nested object (e.g. JSON represented as dict).
    :param path: Ordered keys representing path to the value.
    :return: Deeply nested value (or None).
    """

    n = len(path)
    if n == 0:
        return None

    value = nested_object.get(path[0], None)
    for i in range(1, n):
        if value is None:
            return value
        value = value.get(path[i], None)

    return value


def merge_stock_data_partials(input_dir, output_suffix='_stock_data.json'):
    """ Merge partial stock data files.

    :param input_dir: directory containing partial stock data dumps.
    :param output_suffix: suffix of output file name (will be saved to processed data directory).
    """

    partial_files = [f for f in filter(lambda j: j.endswith('.json'), listdir(input_dir))]
    merged_data = {}

    for pf in partial_files:
        partial_json = json.load(open(join(input_dir, pf), 'r'))
        merged_data.update(partial_json)

    save_json(PROCESSED_DATA_DIR, basename(input_dir) + output_suffix, merged_data, True)


def merge_stock_data_to_master(source_file):
    """ Merge given stock data file to the master file.

    :param source_file: Stock data file with which to update the master file.
    """

    source_json = json.load(open(join(PROCESSED_DATA_DIR, source_file), 'r'))
    master_json = json.load(open(join(PROCESSED_DATA_DIR, 'stock_data_master.json'), 'r'))

    for symbol, symbol_data in source_json.items():
        if symbol not in master_json:
            continue
        for stat_name, stat_value in symbol_data.items():
            master_json[symbol][stat_name] = stat_value

    save_json(PROCESSED_DATA_DIR, 'stock_data_master_updated.json', master_json, sort_keys=True)


def pad_with_median(numbers, n):
    diff = n - len(numbers)
    med = median(numbers)
    return numbers + [med for i in range(diff)]
