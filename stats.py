# pylint: disable=missing-docstring

import math
import pickle
import random
import os
from typing import List, Optional


def get_stats() -> dict:
    if os.path.exists("stats.txt"):
        return pickle.load(open("stats.txt", "rb"))
    else:
        return {}


def save_stats(stats: dict):
    with open("stats.txt", "wb") as f:
        pickle.dump(stats, f)


def get_random_file(directory: str, extension: str = 'jpg') -> str:
    all_files = list_all_files(directory, extension)
    total_count = len(all_files)
    return os.path.join(directory, all_files[random.randint(0, total_count - 1)])


def list_all_files(directory: str, extension: str = 'jpg') -> List[str]:
    all_files = []
    picture_stats = {}
    for _, _, files in os.walk(directory):
        for name in files:
            if extension and name.endswith(extension):
                sanitized_name = name.replace(".{}".format(extension), "")
                count = sanitized_name.split("_")[-1]
                model_name = sanitized_name.replace("_{}".format(count), "")
                cur_count = picture_stats.get(model_name)
                if cur_count is None:
                    cur_count = 0
                picture_stats[model_name] = cur_count + 1
                all_files.append(os.path.join(directory, name))
    save_stats(picture_stats)
    return all_files


def convert_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    index = int(math.floor(math.log(size_bytes, 1024)))
    power = math.pow(1024, index)
    size = round(size_bytes / power, 2)
    return "%s %s" % (size, size_name[index])


def calc_size(directory: str) -> str:
    total_size = 0
    for dirpath, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(dirpath, file)
            total_size += os.path.getsize(filepath)
    return convert_size(total_size)


def parse_and_display_stats(directory: str, format_for_telegram: bool = False) -> Optional[str]:
    total_count = len(list_all_files(directory))
    final_results = ""
    stats = get_stats()
    for key, value in sorted(stats.items()):
        final_results += "{}: {}\n".format(key.replace("_", " "), value)
    final_results += "\nTotal images: {}".format(total_count)
    final_results += "\nTotal models: {}".format(len(stats))
    final_results += "\nTotal size: {}".format(calc_size(directory))
    if not format_for_telegram:
        print(final_results)
        return None
    else:
        return final_results


if __name__ == '__main__':
    print("This script is not intended to be used by itself, use manager.py!")
    exit(1)
