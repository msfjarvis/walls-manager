import os
import math

picture_stats = {}


def walk_dir(directory='.', extension='jpg'):
    total_count = 0
    extension = extension.lower()
    for dirpath, dirnames, files in os.walk(directory):
        for name in files:
            if extension and name.lower().endswith(extension):
                sanitized_name = name.replace(".{}".format(extension), "")
                count = sanitized_name.split("_")[-1]
                model_name = sanitized_name.replace("_{}".format(count), "")
                picture_stats[model_name] = picture_stats.get(model_name, 0) + 1
                total_count += 1
    return total_count


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def calc_size(directory='.'):
    total_size = 0
    for dirpath, dirnames, files in os.walk(directory):
        for f in files:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return convert_size(total_size)


def parse_and_display_stats(directory='.'):
    total_count = walk_dir(directory)
    print("Directory analysis for {}\n".format(directory))
    for key, value in sorted(picture_stats.items()):
        print("{}: {}".format(key.replace("_", " "), value))
    print("\nTotal count: {}".format(total_count))
    print("Total size: {}".format(calc_size(directory)))


if __name__ == '__main__':
    print("This script is not intended to be used by itself, use manager.py!")
    exit(1)
