import json
from os import listdir
from os.path import basename, join
from statistics import median

from src.utils.file_utils import save_json


CONFIG = json.load(open('config.json', 'r'))
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')


def append_if_exists(target_list, value):
    if value is not None:
        target_list.append(value)


def deep_get(nested_object, path, default=None):
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
    merged = {}

    for d in dicts:
        merged.update(d)

    return merged


def merge_stock_data_partials(input_dir, output_suffix='_stock_data.json'):
    partial_files = [f for f in filter(lambda j: j.endswith('.json'), listdir(input_dir))]
    merged_data = {}

    for pf in partial_files:
        partial_json = json.load(open(join(input_dir, pf), 'r'))
        merged_data.update(partial_json)

    save_json(PROCESSED_DATA_DIR, basename(input_dir) + output_suffix, merged_data, True)


def merge_stock_data_to_master(source_file):
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
    return numbers + [med] * diff
