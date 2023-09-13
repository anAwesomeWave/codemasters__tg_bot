import os

from telegram.ext import (Updater,
                          Filters,
                          MessageHandler,
                          CommandHandler,
                          ConversationHandler
                          )
from telegram import ReplyKeyboardMarkup
from telegram.error import TelegramError
from dotenv import load_dotenv

from core.log_conf import create_logger
import core.db
from core.settings import EXPECTED_VALUES

load_dotenv()
logger = create_logger(__name__, 'bot.log')

"""Модуль для управления ботом."""

WORKER_DATA = range(1)
NUMBER_OF_REQUIRED_FIELDS = 4


def worker_data(update, _):
    print('МЫ ТУТ')
    empl_data = update.message.text.split()
    if len(empl_data) != NUMBER_OF_REQUIRED_FIELDS:
        update.message.reply_text(
            'Хммм... Ваше сообщение не соответствует требованиям.'
            'Проверьте, что вы вводите данные корректно(через пробел)'
            'Например:'
            'Тимофей Зубов Разработчик Телеграмм-бот'
        )
    else:
        if core.db.add_employee(
                {
                    EXPECTED_VALUES[i]: empl_data[i]
                    for i in range(NUMBER_OF_REQUIRED_FIELDS)
                }
        ) != 0:
            update.message.reply_text(
                'Что-то пошло не так'
            )
            logger.error('НЕ ЗАПИСАЛИ СОТРУДНИКА! СМОТЕРТЬ ЛОГГЕР БД')
            return ConversationHandler.END
        update.message.reply_text(
            'Отлично! Сотрудник был добавлен!'
        )
    return ConversationHandler.END


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
    add_user_conv = ConversationHandler(
        entry_points=[CommandHandler('add_employee', add_employee)],
        states={
            WORKER_DATA: [MessageHandler(Filters.text, worker_data)],
        },
        fallbacks=[CommandHandler('cancel', cancel_conv)]
    )
    updater.dispatcher.add_handler(add_user_conv)
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


def add_employee(update, context):
    update.message.reply_text(
        'Добавление работника.'
        'Введите данные сотрудника через пробел( его имя, фамилию, занимаеую им должность и проект, над которым он работает).'
        'Остальные данные вы сможете ввести позже.'
    )
    print('Вышли')
    return WORKER_DATA


def cancel_conv(update, context):
    update.message.reply_text('ОТМЕНА')
    return ConversationHandler.END


def start_bot(update, context):
    chat_id = update.effective_chat.id
    buttons = ReplyKeyboardMarkup([
        ['/start', '/add_employee']
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
