import logging
import configparser

from telegram.ext import Updater, CommandHandler
from search import search_files

config = configparser.ConfigParser()
config.read("config.ini")
TOKEN = config["BOT"]["TOKEN"]
LOCAL_DIR = config["SOURCE"]["DIR"]
REMOTE_URL = config["DEST"]["PUBLIC_URL"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename="log.log")


def search(bot, update, args):
    pretty_name, found_files = find_files(args)
    if not found_files:
        update.message.reply_text("No files found for search term '{}'".format(pretty_name))
    else:
        message = "Results for '{}':\n".format(pretty_name)
        for item in iter(sorted(found_files)):
            message += "[{}]({}/{})\n".format(item, REMOTE_URL, item)

        bot.send_message(update.message.chat_id, message, "Markdown", disable_web_page_preview=True)

def find_files(args):
    name = "_".join(args)
    pretty_name = " ".join(args)
    found_files = search_files(name, LOCAL_DIR)
    return pretty_name, found_files

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("search", search, pass_args=True))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
