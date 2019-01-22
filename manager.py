#!/usr/bin/env python3
# pylint: disable=missing-docstring

import argparse
import configparser

from stats import parse_and_display_stats
from sync import sync_to_remote, sync_to_local

config = configparser.ConfigParser()  # pylint: disable=invalid-name
config.read("config.ini")
REMOTE_DIRS = config["DEST"]["RSYNC_DIRS"]
REMOTE_URL = config["DEST"]["PUBLIC_URL"]
LOCAL_DIR = config["SOURCE"]["DIR"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--details", help="List statistics of local directory",
                        action="store_true")
    parser.add_argument("-m", "--markdown", help="Output file names as Markdown links",
                        action="store_true", default=True)
    parser.add_argument("-s", "--sync",
                        help="Set direction of sync, local for pull and remote for push",
                        type=str)
    args = parser.parse_args()

    if args.sync and args.sync == "remote":
        sync_to_remote(REMOTE_DIRS, LOCAL_DIR, args.markdown, REMOTE_URL)
    elif args.sync and args.sync == "local":
        # The adjustments below are required to replicate the sync_to_remote
        # semantics when we do this reverse sync.
        # We choose the first in the REMOTE_DIRS to be our primary and reliable
        # mirror, then append a trailing slash, and remove the same slash
        # from the local directory. Gotta love rsync.
        sync_to_local(REMOTE_DIRS.split(",")[0] + '/', LOCAL_DIR[0:-1])
    elif args.details:
        parse_and_display_stats(LOCAL_DIR)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
