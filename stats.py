# pylint: disable=missing-docstring

import math
import os

PICTURE_STATS = {}


def walk_dir(directory='.', extension='jpg'):
    total_count = 0
    extension = extension.lower()
    for _, _, files in os.walk(directory):
        for name in files:
            if extension and name.lower().endswith(extension):
                sanitized_name = name.replace(".{}".format(extension), "")
                count = sanitized_name.split("_")[-1]
                model_name = sanitized_name.replace("_{}".format(count), "")
                PICTURE_STATS[model_name] = PICTURE_STATS.get(model_name, 0) + 1
                total_count += 1
    return total_count


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    index = int(math.floor(math.log(size_bytes, 1024)))
    power = math.pow(1024, index)
    size = round(size_bytes / power, 2)
    return "%s %s" % (size, size_name[index])


def calc_size(directory='.'):
    total_size = 0
    for dirpath, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(dirpath, file)
            total_size += os.path.getsize(filepath)
    return convert_size(total_size)


def parse_and_display_stats(directory='.', format_for_telegram=False):
    total_count = walk_dir(directory)
    final_results = ""
    for key, value in sorted(PICTURE_STATS.items()):
        final_results += "{}: {}\n".format(key.replace("_", " "), value)
    final_results += "\nTotal images: {}".format(total_count)
    final_results += "\nTotal models: {}".format(len(PICTURE_STATS))
    final_results += "\nTotal size: {}".format(calc_size(directory))
    if not format_for_telegram:
        print(final_results)
    else:
        return final_results


if __name__ == '__main__':
    print("This script is not intended to be used by itself, use manager.py!")
    exit(1)
