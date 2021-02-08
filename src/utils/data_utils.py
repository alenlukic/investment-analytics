import json
from datetime import datetime
from functools import reduce
from os import listdir
from os.path import basename, join
from statistics import median
from time import time

from src.utils.file_utils import save_json


CONFIG = json.load(open('config.json', 'r'))
PROCESSED_DATA_DIR = join(CONFIG['DATA_DIRECTORY'], 'processed')


def append_if_exists(target_list, value):
    if value is not None:
        target_list.append(value)


def compact_object(obj):
    return {k: v for k, v in obj.items() if not is_empty(v)}


def deep_get(nested_object, path, default=None):
    n = len(path)
    if n == 0:
        return default

    value = nested_object
    for i in range(n):
        value = value.get(path[i], None)
        if value is None:
            return default

    return value


def deep_get_keys(nested_object, acc=set()):
    for k in deep_get_values(nested_object).keys():
        acc.add(k)

    return acc


def deep_get_values(nested_object, acc={}):
    if nested_object is None:
        return acc

    for k, v in nested_object.items():
        if type(v) == dict:
            deep_get_values(v, acc)
        else:
            acc[k] = v

    return acc


def get_iso_timestamp(seconds_since_epoch=time()):
    return datetime.isoformat(datetime.fromtimestamp(seconds_since_epoch))


def is_empty(val):
    return val is None or val == [] or val == {} or val == ''


def merge_dictionaries(dicts):
    def update_and_return(target, payload):
        target.update(payload)
        return target

    return reduce(update_and_return, [{}] + dicts)


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
