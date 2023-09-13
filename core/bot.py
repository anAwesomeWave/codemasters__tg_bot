import os

from telegram.ext import Updater, MessageHandler
from dotenv import load_dotenv

from log_conf import create_logger

load_dotenv()
logger = create_logger(__name__, 'bot.log')


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
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # updater.dispatcher.add_handler(
    #     MessageHandler(Filters.sticker, get_id_of_sticker)
    # )
    # serve()

    logger.debug('test')
    try:
        updater = prepare_bot()
    except Exception as e:
        logger.error(e)
