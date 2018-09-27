import os

picture_stats = {}


def walk_dir(directory='.', extension='jpg'):
    global total_count
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


def parse_and_display_stats(directory='.'):
    walk_dir(directory)
    print("Directory analysis for {}\n".format(directory))
    for key, value in sorted(picture_stats.items()):
        print("{}: {}".format(key.replace("_", " "), value))
    print("\nTotal: {}".format(total_count))


if __name__ == '__main__':
    print("This script is not intended to be used by itself, use manager.py!")
    exit(1)
