import json
from os import makedirs
from os.path import exists, join


def touch(file_name):
    """ Create file if it doesn't exist.

    :param file_name: name of the file to create.
    """
    open(file_name, 'a').close()


def create_directory(directory_name):
    """ Create the directory if it doesn't exist.

    :param directory_name: name of the directory to create.
    """

    if not exists(directory_name):
        makedirs(directory_name)


def save_file(output_dir, file_name, content, mode='w'):
    """ Saves content to specified file name in specified directory.

    :param output_dir: output directory where file should be saved.
    :param file_name: name of the file.
    :param content: content to write to the file.
    :param mode: mode in which to open the file pointer.
    """

    with open(join(output_dir, file_name), mode) as w:
        w.write(content)


def update_file(output_dir, file_name, content):
    """ Append content to specified file.

    :param output_dir: output directory of file to be updated.
    :param file_name: name of the file to be updated.
    :param content: content to append to the file.
    """
    save_file(output_dir, file_name, content, 'a')


def save_json(output_dir, file_name, content, sort_keys=False, indent=2, mode='w'):
    """ Saves JSON object to specified file name in specified directory.

    :param output_dir: output directory where file should be saved.
    :param file_name: name of the file to be saved.
    :param content: content to append to the file.
    :param sort_keys: indicates whether to write JSON in sorted key order.
    :param indent: number of spaces to indent subsequent levels of nesting in the JSON.
    :param mode: mode in which to open the file pointer.
    """

    json_path = join(output_dir, file_name)
    touch(json_path)
    with open(json_path, 'r+') as w:
        previous_content = {} if mode != 'a' else json.load(w)
        content.update(previous_content)
        json.dump(content, w, sort_keys=sort_keys, indent=indent)


def update_json(output_dir, file_name, content, sort_keys=False, indent=2):
    """ Merge JSON object with existing JSON object on disk.

    :param output_dir: output directory of file to be updated.
    :param file_name: name of the file to be updated.
    :param content: JSON object to merge to the file.
    :param sort_keys: indicates whether to write JSON in sorted key order.
    :param indent: number of spaces to indent subsequent levels of nesting in the JSON
    """
    save_json(output_dir, file_name, content, sort_keys, indent, 'a')
