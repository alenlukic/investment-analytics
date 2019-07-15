import json
from os import listdir
from os.path import basename, join
from statistics import median

from src.utils.file_utils import save_json


CONFIG = json.load(open('config.json', 'r'))
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')


def append_if_exists(target_list, value):
    """ Appends value to the list if it's not None.

    :param target_list: list to append value to.
    :param value: the potential value.
    """

    if value is not None:
        target_list.append(value)


def deep_get(nested_object, path, default=None):
    """ Gets deeply nested value from object.

    :param nested_object: deeply nested object (e.g. JSON represented as dict).
    :param path: ordered keys representing path to the value.
    :param default: (optional) default value to return if value is missing.
    :return: deeply nested value.
    """

    n = len(path)
    if n == 0:
        return default

    value = nested_object.get(path[0], None)
    for i in range(1, n):
        if value is None:
            return default
        value = value.get(path[i], None)

    return value


def merge_dictionaries(dicts):
    """ Merges the given list of dictionaries. Note: if duplicate keys exist across the dicts, then only the value of
    the last such key seen will be preserved.

    :param dicts: list of dictionaries to merge.
    :return: merged dictionary.
    """

    merged = {}

    for d in dicts:
        merged.update(d)

    return merged


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

    :param source_file: stock data file with which to update the master file.
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
    """ Pad missing values using the median of known values.

    :param numbers: set of known values.
    :param n: total number of values (known + unknown).
    :returns: values padded with median.
    """

    diff = n - len(numbers)
    med = median(numbers)
    return numbers + [med] * diff
