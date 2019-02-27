#!/usr/bin/env python3
# pylint: disable=missing-docstring

import configparser
import logging
import os
from random import randint

import pickledb
from telegram import ChatAction
from telegram.error import BadRequest, TimedOut
from telegram.ext import Updater, CommandHandler
from telegram.ext.dispatcher import run_async

from decorators import send_action, restricted
from file_helpers import find_files, md5, get_base_name
from stats import parse_and_display_stats, get_random_file as random_file

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name
database = pickledb.load("tg_file_ids.db", True)  # pylint: disable=invalid-name
config = configparser.ConfigParser()  # pylint: disable=invalid-name
config.read("config.ini")
TOKEN = config["BOT"]["TOKEN"]
LOCAL_DIR = config["SOURCE"]["DIR"]
REMOTE_URL = config["DEST"]["PUBLIC_URL"]
PHOTO_SIZE_THRESHOLD = 5242880  # 5mB, from Telegram documentation.


@run_async
def get(bot, update, args):
    file_path, caption = get_file_and_caption(update, args)
    if not file_path and not caption:
        return
    if (os.path.getsize(file_path)) > PHOTO_SIZE_THRESHOLD:
        upload_document(bot, update, file_path, caption)
    else:
        upload_photo(bot, update, file_path, caption)


@run_async
def get_file(bot, update, args):
    file_path, caption = get_file_and_caption(update, args)
    upload_document(bot, update, file_path, caption)


@restricted
@send_action(ChatAction.UPLOAD_DOCUMENT)
def get_log(bot, update):
    del bot
    update.message.reply_document(document=open("log.log", "rb"),
                                  quote=True)


@run_async
@send_action(ChatAction.TYPING)
def search(bot, update, args):
    del bot
    if not args:
        update.message.reply_text("Please specify who to search for!", quote=True)
        return
    pretty_name, found_files = find_files(args, LOCAL_DIR)
    if not found_files:
        update.message.reply_text("No files found for search term '{}'".format(pretty_name),
                                  quote=True)
    else:
        message = "Results for '{}':\n".format(pretty_name)
        for item in iter(sorted(found_files)):
            message += "[{0}]({1}{0})\n".format(item, REMOTE_URL)

        update.message.reply_text(message, "Markdown", disable_web_page_preview=True,
                                  quote=True)


@run_async
@restricted
@send_action(ChatAction.TYPING)
def get_stats(bot, update):
    del bot
    update.message.reply_text(parse_and_display_stats(LOCAL_DIR, True),
                              parse_mode="Markdown",
                              quote=True)

@run_async
def get_random_file(bot, update):
    file = random_file(LOCAL_DIR)
    upload_photo(bot, update, file, get_caption(get_base_name(file)))


def upload_photo(bot, update, file_path, caption):
    file_hash = md5(file_path)
    telegram_id = database.get(file_hash)
    message = upload_photo_internal(bot, update, file_path, caption, telegram_id)
    if message:
        database.set(file_hash, message.photo[0].file_id)


@send_action(ChatAction.UPLOAD_DOCUMENT)
def upload_document(bot, update, file_path, caption):
    file_hash = md5(file_path)
    telegram_id = database.get(file_hash)
    message = upload_document_internal(bot, update, file_path, caption, telegram_id)
    if message:
        database.set(file_hash, message.document.file_id)


@send_action(ChatAction.UPLOAD_PHOTO)
def upload_photo_internal(bot, update, file, caption, telegram_id=None):
    try:
        if telegram_id:
            update.message.reply_photo(photo=telegram_id,
                                       caption=caption,
                                       parse_mode="Markdown",
                                       quote=True)
            return None
        return update.message.reply_photo(photo=open(file, "rb"),
                                          caption=caption,
                                          parse_mode="Markdown",
                                          quote=True)
    except TimedOut:
        logger.error("Timed out in upload_photo_internal")
    except BadRequest:
        logger.error("BadRequest raised in upload_photo_internal, falling back to document")
        return upload_document_internal(bot, update, file, caption, telegram_id)
    return None


@send_action(ChatAction.UPLOAD_DOCUMENT)
def upload_document_internal(bot, update, file, caption, telegram_id=None):
    del bot
    try:
        if telegram_id:
            update.message.reply_document(document=telegram_id,
                                          caption=caption,
                                          parse_mode="Markdown",
                                          quote=True)
        else:
            return update.message.reply_document(document=open(file, 'rb'),
                                                 caption=caption,
                                                 parse_mode="Markdown",
                                                 quote=True)
    except TimedOut:
        logger.error("Timed out in upload_document_internal")
    return None


# pylint: disable=inconsistent-return-statements
def get_file_and_caption(update, args):
    if not args:
        update.message.reply_text("Please specify who to search for!", quote=True)
        return
    pretty_name, found_files = find_files(args, LOCAL_DIR)
    if not found_files:
        update.message.reply_text("No files found for search term '{}'".format(pretty_name),
                                  quote=True)
        return None, None
    selected_name = found_files[randint(0, len(found_files) - 1)]
    selected_file_path = '{}/{}'.format(LOCAL_DIR, selected_name)
    caption = get_caption(selected_name)
    return selected_file_path, caption


def get_caption(file_name, remote_url=REMOTE_URL):
    return "[{0}]({1}{0})".format(file_name, remote_url)


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
    dispatcher.add_handler(CommandHandler("pic", get, pass_args=True))
    dispatcher.add_handler(CommandHandler("getfile", get_file, pass_args=True))
    dispatcher.add_handler(CommandHandler("log", get_log))
    dispatcher.add_handler(CommandHandler("search", search, pass_args=True))
    dispatcher.add_handler(CommandHandler("stats", get_stats))
    dispatcher.add_handler(CommandHandler("random", get_random_file))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
