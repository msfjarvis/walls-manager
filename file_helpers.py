#!/usr/bin/env python3
# pylint: disable=missing-docstring
import hashlib

from search import search_files
from string_helpers import capitalize


def find_files(args, dir_name):
    args_copy = []
    for arg in iter(args):
        args_copy.append(capitalize(arg))
    name = "_".join(args_copy)
    pretty_name = " ".join(args)
    found_files = search_files(name, dir_name)
    return pretty_name, found_files


def md5(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(2 ** 20), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
