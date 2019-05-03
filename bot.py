#!/usr/bin/env python3
# pylint: disable=missing-docstring

import configparser
import logging
import os
from copy import deepcopy
from random import randint
from signal import signal, SIGTERM, SIGINT

import pickledb
from telegram import ChatAction
from telegram.error import BadRequest, TimedOut, TelegramError
from telegram.ext import Updater, CommandHandler
from telegram.ext.dispatcher import run_async

from decorators import send_action, restricted
from file_helpers import find_files, md5, get_base_name
from stats import parse_and_display_stats, list_all_files, get_random_file as random_file

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


@run_async
@restricted
@send_action(ChatAction.UPLOAD_DOCUMENT)
def get_log(bot, update):
    del bot
    update.message.reply_document(document=open("log.log", "rb"),
                                  quote=True)


@run_async
@restricted
@send_action(ChatAction.TYPING)
def get_db_stats(bot, update):
    del bot
    db_stats = "Database statistics\n\n"
    db_stats += f"Total keys: {database.totalkeys()}"
    update.message.reply_text(db_stats, quote=True)


@run_async
@restricted
def validate_db_entries(bot, update):
    purged_entries = 0
    db_copy = deepcopy(database)
    for key in db_copy.getall():
        file_hash = key
        tg_file_id = db_copy.get(key)
        try:
            bot.get_file(tg_file_id)
        except TelegramError:
            logger.error("Found missing file, purging from database")
            database.rem(file_hash)
            purged_entries += 1
    update.message.reply_text(f"Finished database validation, found {purged_entries} invalid entries",
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
        update.message.reply_text(f"No files found for search term '{pretty_name}'",
                                  quote=True)
    else:
        message = f"Results for '{pretty_name}':\n"
        for item in iter(sorted(found_files)):
            message += f"[{item}]({REMOTE_URL}{item})\n"

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


@run_async
@restricted
def populate_cache(bot, update):
    all_files = list_all_files(LOCAL_DIR)
    for file in all_files:
        file_hash = md5(file)
        if database.exists(file_hash):
            continue
        message = upload_photo_internal(bot, update, file, get_caption(get_base_name(file)))
        add_entry_to_database(file_hash, message)
    update.message.reply_text(f"Done populating cache, db now has {database.totalkeys()} entries!")


def upload_photo(bot, update, file_path, caption):
    file_hash = md5(file_path)
    telegram_id = database.get(file_hash)
    message = upload_photo_internal(bot, update, file_path, caption, telegram_id)
    add_entry_to_database(file_hash, message)


@send_action(ChatAction.UPLOAD_DOCUMENT)
def upload_document(bot, update, file_path, caption):
    file_hash = md5(file_path)
    telegram_id = database.get(file_hash)
    message = upload_document_internal(bot, update, file_path, caption, telegram_id)
    add_entry_to_database(file_hash, message)


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
    except BadRequest:
        logger.error("BadRequest raised in upload_photo_internal, falling back to document")
        return upload_document_internal(bot, update, file, caption, telegram_id)
    except TimedOut:
        logger.error("Timed out in upload_photo_internal")
    except Exception as e:
        logger.error(e)
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
    except Exception as e:
        logger.error(e)
    return None


def add_entry_to_database(file_hash, message):
    if not message:
        logger.debug("NoneType message passed to add_entry_to_database")
    elif message.document:
        database.set(file_hash, message.document.file_id)
    elif message.photo:
        database.set(file_hash, message.photo[0].file_id)


def get_file_and_caption(update, args):
    if not args:
        update.message.reply_text("Please specify who to search for!", quote=True)
        return None, None
    pretty_name, found_files = find_files(args, LOCAL_DIR)
    if not found_files:
        update.message.reply_text(f"No files found for search term '{pretty_name}'", quote=True)
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


def handle_exit(*args):
    del args
    database.dump()


def main():
    for sig in (SIGTERM, SIGINT):
        signal(sig, handle_exit)
    configure_logging()
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("cache", populate_cache))
    dispatcher.add_handler(CommandHandler("dbstats", get_db_stats))
    dispatcher.add_handler(CommandHandler("getfile", get_file, pass_args=True))
    dispatcher.add_handler(CommandHandler("log", get_log))
    dispatcher.add_handler(CommandHandler("pic", get, pass_args=True))
    dispatcher.add_handler(CommandHandler("random", get_random_file))
    dispatcher.add_handler(CommandHandler("search", search, pass_args=True))
    dispatcher.add_handler(CommandHandler("stats", get_stats))
    dispatcher.add_handler(CommandHandler("validate", validate_db_entries))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
