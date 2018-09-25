#!/usr/bin/env python3.7
import argparse
import configparser

from stats import parse_and_display_stats
from sync import sync_to_remote

config = configparser.ConfigParser()
config.read("config.ini")
rsync_dirs = config["DEST"]["RSYNC_DIRS"]
source = config["SOURCE"]["DIR"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sync", help="Sync local directory to remote destination",
                        action="store_true")
    parser.add_argument("-d", "--details", help="List statistics of local directory",
                        action="store_true")
    args = parser.parse_args()

    if args.sync:
        sync_to_remote(rsync_dirs, source)
    elif args.details:
        parse_and_display_stats(source)


if __name__ == '__main__':
    main()
