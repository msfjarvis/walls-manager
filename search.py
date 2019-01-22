import os


def search_files(file_name, directory='.'):
    found_files = []
    for _, _, files in os.walk(directory):
        for name in files:
            if file_name and name.startswith(file_name):
                found_files.append(name)
    if len(found_files) > 0:
        return found_files
    else:
        return None
