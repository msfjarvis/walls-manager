#!/usr/bin/env python3
# pylint: disable=missing-docstring


def capitalize(string: str) -> str:
    chars = list(string)
    chars[0] = chars[0].upper()
    return "".join(chars)
