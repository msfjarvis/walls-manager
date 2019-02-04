#!/usr/bin/env python3
# pylint: disable=missing-docstring


def capitalize(string):
    chars = list(string)
    chars[0] = chars[0].upper()
    return "".join(chars)
