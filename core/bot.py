import os

from telegram.ext import Updater, MessageHandler
from dotenv import load_dotenv

from log_conf import create_logger

load_dotenv()
logger = create_logger(__name__, 'bot.log')

"""Модуль для управления ботом."""


def prepare_bot():
    try:
        updater = Updater(token=os.getenv('API_KEY'))
        logger.debug("Initialized bot successfully.")
    except ValueError:
        message = 'Cannot initialize bot.\nCreate ".env" in a root dir and provide your "API_KEY"'
        raise Exception(
            message
        )
    return updater


def serve():
    try:
        updater = prepare_bot()
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(e)



if __name__ == '__main__':
    # updater.dispatcher.add_handler(
    #     MessageHandler(Filters.sticker, get_id_of_sticker)
    # )
    # serve()

    try:
        updater = prepare_bot()
    except Exception as e:
        logger.error(e)