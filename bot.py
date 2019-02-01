#!/usr/bin/env python3
# pylint: disable=missing-docstring

import configparser
import logging
import os
from random import randint

from telegram import ChatAction
from telegram.error import BadRequest
from telegram.ext import Updater, CommandHandler

from decorators import send_action, restricted
from search import search_files

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name
config = configparser.ConfigParser()  # pylint: disable=invalid-name
config.read("config.ini")
TOKEN = config["BOT"]["TOKEN"]
LOCAL_DIR = config["SOURCE"]["DIR"]
REMOTE_URL = config["DEST"]["PUBLIC_URL"]
PHOTO_SIZE_THRESHOLD = 5242880  # 5mB, from Telegram documentation.


@send_action(ChatAction.TYPING)
def search(bot, update, args):
    del bot
    if not args:
        update.message.reply_text("Please specify who to search for!", quote=True)
        return
    pretty_name, found_files = find_files(args)
    if not found_files:
        update.message.reply_text("No files found for search term '{}'".format(pretty_name),
                                  quote=True)
    else:
        message = "Results for '{}':\n".format(pretty_name)
        for item in iter(sorted(found_files)):
            message += "[{0}]({1}/{0})\n".format(item, REMOTE_URL)

        update.message.reply_text(message, "Markdown", disable_web_page_preview=True,
                                  quote=True)


def upload_photo(bot, update, file_path, caption):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)
    update.message.reply_photo(photo=open(file_path, 'rb'),
                               caption=caption,
                               parse_mode="Markdown",
                               quote=True)


def upload_document(bot, update, file_path, caption):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_DOCUMENT)
    update.message.reply_document(document=open(file_path, 'rb'),
                                  caption=caption,
                                  parse_mode="Markdown",
                                  quote=True)


def get_file_and_caption(update, args):
    if not args:
        update.message.reply_text("Please specify who to search for!", quote=True)
        return
    pretty_name, found_files = find_files(args)
    if not found_files:
        update.message.reply_text("No files found for search term '{}'".format(pretty_name),
                                  quote=True)
    else:
        selected_name = found_files[randint(0, len(found_files) - 1)]
        selected_file_path = '{}/{}'.format(LOCAL_DIR, selected_name)
        caption = "[{0}]({1}/{0})".format(selected_name, REMOTE_URL)
    return selected_file_path, caption


def get(bot, update, args):
    file_path, caption = get_file_and_caption(update, args)
    if (os.path.getsize(file_path)) > PHOTO_SIZE_THRESHOLD:
        upload_document(bot, update, file_path, caption)
    else:
        try:
            upload_photo(bot, update, file_path, caption)
        except BadRequest:
            logger.debug("BadRequest caught during upload_photo, falling back to document")
            upload_document(bot, update, file_path, caption)


def get_file(bot, update, args):
    file_path, caption = get_file_and_caption(update, args)
    upload_document(bot, update, file_path, caption)


@restricted
@send_action(ChatAction.UPLOAD_DOCUMENT)
def get_log(bot, update):
    del bot
    update.message.reply_document(document=open("log.log", "rb"),
                                  quote=True)


def find_files(args):
    args_copy = []
    for arg in iter(args):
        args_copy.append(capitalize(arg))
    name = "_".join(args_copy)
    pretty_name = " ".join(args)
    found_files = search_files(name, LOCAL_DIR)
    return pretty_name, found_files


def capitalize(string):
    chars = list(string)
    chars[0] = chars[0].upper()
    return "".join(chars)


def configure_logging():
    if os.getenv("DEBUG", "") != "":
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG,
                            filename="log.log")


def main():
    configure_logging()
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("search", search, pass_args=True))
    dispatcher.add_handler(CommandHandler("get", get, pass_args=True))
    dispatcher.add_handler(CommandHandler("getfile", get_file, pass_args=True))
    dispatcher.add_handler(CommandHandler("log", get_log))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
