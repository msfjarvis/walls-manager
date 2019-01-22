#!/usr/bin/env python3
# pylint: disable=missing-docstring

import os


def search_files(file_name, directory='.'):
    found_files = []
    for _, _, files in os.walk(directory):
        for name in files:
            if file_name and name.startswith(file_name):
                found_files.append(name)
    if not found_files:
        return None
    return found_files
