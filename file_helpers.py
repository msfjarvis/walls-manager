#!/usr/bin/env python3
# pylint: disable=missing-docstring
import hashlib
from typing import List, Tuple

from search import search_files
from string_helpers import capitalize


def find_files(args: List[str], dir_name: str) -> Tuple[str, List[str]]:
    args_copy = []
    for arg in iter(args):
        args_copy.append(capitalize(arg))
    pretty_name = " ".join(args)
    found_files = search_files(pretty_name.lower(), dir_name)
    return pretty_name, found_files


def md5(file_name: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as full_file:
        for chunk in iter(lambda: full_file.read(2 ** 20), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_base_name(file_path: str) -> str:
    return file_path.split("/")[-1]
