from telegram.ext import Updater
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
TOKEN=config["BOT"]["TOKEN"]

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
