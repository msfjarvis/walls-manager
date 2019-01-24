#!/usr/bin/env python3
# pylint: disable=missing-docstring

import configparser
import logging
from random import randint

from telegram import ChatAction
from telegram.ext import Updater, CommandHandler

from decorators import send_action
from search import search_files

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name
config = configparser.ConfigParser()  # pylint: disable=invalid-name
config.read("config.ini")
TOKEN = config["BOT"]["TOKEN"]
LOCAL_DIR = config["SOURCE"]["DIR"]
REMOTE_URL = config["DEST"]["PUBLIC_URL"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,
                    filename="log.log")


@send_action(ChatAction.TYPING)
def search(bot, update, args):
    if not args:
        update.message.reply_text("Please specify who to search for!", quote=True)
        return
    pretty_name, found_files = find_files(args)
    if not found_files:
        update.message.reply_text("No files found for search term '{}'".format(pretty_name), quote=True)
    else:
        message = "Results for '{}':\n".format(pretty_name)
        for item in iter(sorted(found_files)):
            message += "[{0}]({1}/{0})\n".format(item, REMOTE_URL)

        update.message.reply_text(message, "Markdown", disable_web_page_preview=True, quote=True)


@send_action(ChatAction.UPLOAD_PHOTO)
def get(bot, update, args):
    if not args:
        update.message.reply_text("Please specify who to search for!", quote=True)
        return
    pretty_name, found_files = find_files(args)
    if not found_files:
        update.message.reply_text("No files found for search term '{}'".format(pretty_name), quote=True)
    else:
        selected_name = found_files[randint(0, len(found_files) - 1)]
        selected_file_path = '{}/{}'.format(LOCAL_DIR, selected_name)
        caption = "[{0}]({1}/{0})".format(selected_name, REMOTE_URL)
        update.message.reply_photo(photo=open(selected_file_path, 'rb'),
                                   caption=caption,
                                   parse_mode="Markdown",
                                   quote=True)


def find_files(args):
    args_copy = []
    for arg in iter(args):
        args_copy.append(arg.lower().capitalize())
    name = "_".join(args_copy)
    pretty_name = " ".join(args)
    found_files = search_files(name, LOCAL_DIR)
    return pretty_name, found_files


def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("search", search, pass_args=True))
    dispatcher.add_handler(CommandHandler("get", get, pass_args=True))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
