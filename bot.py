#!/usr/bin/env python3
# pylint: disable=missing-docstring

import configparser
import logging

from telegram.ext import Updater, CommandHandler

from search import search_files

config = configparser.ConfigParser()  # pylint: disable=invalid-name
config.read("config.ini")
TOKEN = config["BOT"]["TOKEN"]
LOCAL_DIR = config["SOURCE"]["DIR"]
REMOTE_URL = config["DEST"]["PUBLIC_URL"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename="log.log")


def search(bot, update, args):
    name = "_".join(args)
    pretty_name = " ".join(args)
    found_files = search_files(name, LOCAL_DIR)
    if not found_files:
        update.message.reply_text("No files found for search term '{}'".format(pretty_name))
    else:
        message = "Results for '{}':\n".format(pretty_name)
        for item in iter(sorted(found_files)):
            message += "[{0}]({1}/{0})\n".format(item, REMOTE_URL)

        bot.send_message(update.message.chat_id, message, "Markdown", disable_web_page_preview=True)


def main():
    updater = Updater(TOKEN)
    updater.dispatcher.add_handler(CommandHandler("search", search, pass_args=True))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
