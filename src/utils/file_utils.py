import json
from os import makedirs
from os.path import exists, join

from src.definitions.config import TICKER_SYMBOLS


def touch(file_name):
    open(file_name, 'a').close()


def create_directory(directory_name):
    if not exists(directory_name):
        makedirs(directory_name)


def save_file(output_dir, file_name, content, mode='w'):
    with open(join(output_dir, file_name), mode) as w:
        w.write(content)


def update_file(output_dir, file_name, content):
    save_file(output_dir, file_name, content, 'a')


def save_json(output_dir, file_name, content, sort_keys=False, indent=2, mode='w'):
    json_path = join(output_dir, file_name)
    touch(json_path)
    with open(json_path, 'r+') as w:
        previous_content = {} if mode != 'a' else json.load(w)
        content.update(previous_content)
        json.dump(content, w, sort_keys=sort_keys, indent=indent)


def update_json(output_dir, file_name, content, sort_keys=False, indent=2):
    save_json(output_dir, file_name, content, sort_keys, indent, 'a')


def load_stock_symbols():
    with open(TICKER_SYMBOLS, 'r') as tf:
        return [s.strip() for s in tf.readlines()]
