#!/usr/bin/env python3
# pylint: disable=missing-docstring

import os
from typing import List


def search_files(file_name: str, directory: str = ".") -> List[str]:
    found_files = []
    for _, _, files in os.walk(directory):
        for name in files:
            if file_name in name.lower().replace("_", " "):
                found_files.append(name)
    return found_files
