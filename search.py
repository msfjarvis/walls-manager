#!/usr/bin/env python3
# pylint: disable=missing-docstring

import os
from os.path import splitext
from typing import List


def search_files(file_name: str, directory: str = '.') -> List[str]:
    found_files = []
    for _, _, files in os.walk(directory):
        for name in files:
            items = splitext(name.lower())[0].split("_")
            for item in items:
                if item == file_name or item.startswith(file_name):
                    found_files.append(name)
    return found_files
