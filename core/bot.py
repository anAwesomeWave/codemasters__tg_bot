import os

from telegram.ext import Updater, MessageHandler, CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram.error import TelegramError
from dotenv import load_dotenv

from core.log_conf import create_logger

load_dotenv()
logger = create_logger(__name__, 'bot.log')

"""Модуль для управления ботом."""


def prepare_bot():
    try:
        updater = Updater(token=os.getenv('API_KEY'))
        logger.debug("Initialized bot successfully.")
    except ValueError:
        message = (
            'Cannot initialize bot.\nCreate ".env" in a root dir and provide your "API_KEY"')
        raise Exception(
            message
        )
    updater.dispatcher.add_handler(CommandHandler('start', start_bot))
    return updater


def send_message(bot, chat_id, message, **kwargs):
    try:
        bot.send_message(
            chat_id=chat_id,
            text=message,
            **kwargs
        )
    except Exception as e:
        logger.critical(f'BOT CANNOT SEND A MESSAGE!\n{e}', exc_info=1)


def start_bot(update, context):
    chat_id = update.effective_chat.id
    buttons = ReplyKeyboardMarkup([
        ['/start']
    ], resize_keyboard=True)
    send_message(
        context.bot,
        chat_id,
        'Бот успешно стартовал',
        reply_markup=buttons
    )


def serve():
    try:
        updater = prepare_bot()
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    serve()
