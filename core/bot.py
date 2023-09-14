import os
from datetime import datetime
from io import BytesIO, BufferedReader

import pytz

from telegram.ext import (
    Updater,
    Filters,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
)
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from core.log_conf import create_logger
import core.db
from core.settings import EXPECTED_VALUES, ALL_DB_COLUMNS
from core.utils import employee_card_message

load_dotenv()
logger = create_logger(__name__, 'bot.log')

"""Модуль для управления ботом."""

WORKER_DATA = range(1)
ENTER_ID, UPDATE_FIELD, UPDATE_VAL = range(3)

UPDATE_END_VAL = range(1)
FIND_ID = range(1)
NUMBER_OF_REQUIRED_FIELDS = 4


def worker_data(update, _):
    empl_data = update.message.text.split()
    if len(empl_data) != NUMBER_OF_REQUIRED_FIELDS:
        update.message.reply_text(
            'Хммм... Ваше сообщение не соответствует требованиям.'
            'Проверьте, что вы вводите данные корректно(через пробел)'
            'Например:'
            'Тимофей Зубов Разработчик Телеграмм-бот'
        )
    else:
        data = {EXPECTED_VALUES[i]: empl_data[i] for i in range(NUMBER_OF_REQUIRED_FIELDS)}
        data.update({'time': datetime.now(pytz.utc)})
        employee_id = core.db.add_employee(data)
        try:
            update.message.reply_text(
                f'Отлично! Сотрудник был добавлен! Eго ID - {employee_id}'
            )
        except TypeError as e:
            update.message.reply_text(
                'Что-то пошло не так'
            )
            logger.error('НЕ ЗАПИСАЛИ СОТРУДНИКА! СМОТЕРТЬ ЛОГГЕР БД')
    return ConversationHandler.END


def update_enter_id(update, context):
    update.message.reply_text(
        'Введите ID сотрудника, которого вы хотите изменить.')
    try:
        id = int(update.message.text.strip())
    except ValueError:
        update.message.reply_text('Введите число')
    found_employee = core.db.get_user_by_id(id)
    if found_employee is None:
        update.message.reply_text(
            'К сожалению, пользователь не найден. Убедитесь, что вы вводите Корректный идентификатор(число).')
        return ConversationHandler.END
    update.message.reply_text('Пользователь найден!')
    text_update_col = [x for x in ALL_DB_COLUMNS if x not in ('ID',)]
    # reply_keyboard = [['/update ' + x for x in
    #                    text_update_col] + ['/update_avatar', ]]
    n = len(text_update_col) // 2
    reply_keyboard = [
        [
            InlineKeyboardButton(f'{x}', callback_data=f'{id} {x}') for x in text_update_col[:n]
        ],
        [
            InlineKeyboardButton(f'{x}', callback_data=f'{id} {x}') for x
            in text_update_col[n:]

        ]
    ]

    employee_card, avatar_detected = employee_card_message(found_employee)
    if avatar_detected:
        photo = BufferedReader(BytesIO(found_employee[-2]))
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=employee_card)
    else:
        update.message.reply_text(employee_card, reply_markup=InlineKeyboardMarkup(reply_keyboard))
    return ConversationHandler.END


def update_text_field(update, context):
    query = update.callback_query

    query.answer()
    data = query.data.split()
    send_message(
        context.bot,
        update.effective_chat.id,
        f'Вы хотите поменять поле {data[1]} у работника с ID {data[0]}\n'
        f'Введите новое значение или команду /cancel для отмены'
    )
    context.user_data['id'] = data[0]
    context.user_data['field_to_update'] = data[1]
    return UPDATE_END_VAL


def update_text_field_val(update, context):
    new_val = update.message.text
    if context.user_data['field_to_update'] == 'avatar':
        update.message.reply_text('в avatar нельзя записать текст')
        return ConversationHandler.END
    status = core.db.update_field(context.user_data['id'], {context.user_data['field_to_update']: new_val})
    if status == 0:
        update.message.reply_text('Вы изменили поле!')
    else:
        update.message.reply_text('Что-то не так...')
    return ConversationHandler.END


def update_avatar_val(update, context):
    if context.user_data['field_to_update'] != 'avatar':
        update.message.reply_text('фото можно добавить только в поле avatar.')
        return ConversationHandler.END
    update.message.reply_text('ВСЕ ОК')
    file = context.bot.get_file(update.message.photo[-1].file_id)
    f = BytesIO(file.download_as_bytearray()).getbuffer().tobytes()
    ans = core.db.update_field(context.user_data['id'], {'avatar': f})
    if ans == 0:
        update.message.reply_text('ВСЕ ОК')
    else:
        update.message.reply_text('Не добавили')

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
            WORKER_DATA: [MessageHandler(Filters.text & (~ Filters.command), worker_data)],
        },
        fallbacks=[CommandHandler('cancel', cancel_conv)]
    )
    find_by_id_conv = ConversationHandler(
        entry_points=[CommandHandler('find_by_id', send_find_by_id)],
        states={
            FIND_ID: [MessageHandler(Filters.text & (~ Filters.command), send_find_by_id_end)],
        },
        fallbacks=[CommandHandler('cancel', cancel_conv)]
    )
    update_employee_field_start = ConversationHandler(
        entry_points=[CommandHandler('update_employee', update_employee)],
        states={
            ENTER_ID: [MessageHandler(Filters.text & (~ Filters.command), update_enter_id)],

        },
        fallbacks=[CommandHandler('cancel', cancel_conv)]
    )
    update_employee_field_end = ConversationHandler(
        entry_points=[CallbackQueryHandler(update_text_field)],
        states={
            UPDATE_END_VAL: [
                MessageHandler(Filters.text & (~ Filters.command), update_text_field_val),
                MessageHandler(Filters.photo & (~ Filters.command), update_avatar_val),
            ],

        },
        fallbacks=[CommandHandler('cancel', cancel_conv)]
    )
    updater.dispatcher.add_handler(add_user_conv)
    updater.dispatcher.add_handler(update_employee_field_start)
    updater.dispatcher.add_handler(update_employee_field_end)
    updater.dispatcher.add_handler(find_by_id_conv)
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
        'Остальные данные вы сможете ввести позже. Также вы моежете ввести /cancel для отмены'
    )
    return WORKER_DATA

def send_find_by_id(update, context):
    update.message.reply_text('Введите ID сотрудника для продеолжения или cancel для отмены')
    return FIND_ID

def send_find_by_id_end(update, context):
    try:
        id = int(update.message.text)
        found_employee = core.db.get_user_by_id(id)
        if found_employee is not None:
            card_message=employee_card_message(found_employee)
            if card_message[1]:
                photo = BufferedReader(BytesIO(found_employee[-2]))
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=card_message[0])
            else:
                update.message.reply_text(card_message[0])
    except ValueError as e:
        update.message.reply_text("Введите число")
    except Exception as e:
        logger.error(e)

    return ConversationHandler.END
def update_employee(update, context):
    update.message.reply_text(
        'Обновление данных работника.'
        'Введите ID работника. Или /cancel для отмены'
    )
    return ENTER_ID


def cancel_conv(update, context):
    update.message.reply_text('ОТМЕНА')
    return ConversationHandler.END


def start_bot(update, context):
    chat_id = update.effective_chat.id
    send_message(
        context.bot,
        chat_id,
        'Бот успешно стартовал',
        reply_markup=ReplyKeyboardMarkup([
            core.settings.BASIC_BOT_COMMANDS
        ], resize_keyboard=True)
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
