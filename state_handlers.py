from bot_utils import bot
from aiogram.dispatcher import FSMContext
from aiogram import types
import re
from database import add_service_name_to_db, add_key_to_db


# Функции обработки вводимых данных по машине состояний
async def handle_rename_service(message: types.Message, state: FSMContext):
    column_number = (await state.get_data()).get('column_number')
    await filter_service_name(message, message.chat.id, column_number)
    await state.finish()


async def handle_enter_key(message: types.Message, state: FSMContext):
    column_number = (await state.get_data()).get('column_number')
    await filter_key(message, message.chat.id, column_number)
    await state.finish()


# Функции обработки вводимого пользователем текста для сервиса
async def filter_service_name(message, user_id, code_number):
    name = message.text
    if len(name) > 32:
        await bot.send_message(user_id, text="Название не может содержать в себе более 32 символов!")
    else:
        name = re.sub(r'[\-]', '', name)
        await bot.send_message(user_id, text="Название сервиса изменено успешно!")
        add_service_name_to_db(name, user_id, code_number)


# Функции обработки вводимого пользователем текста для ключа
async def filter_key(message, user_id, code_number):
    key = message.text
    pattern = r'^[A-Za-z2-7\- ]+$'
    if not re.match(pattern, key):
        await bot.send_message(user_id, text="Ключ введен неверно! Ключ должен содержать в себе символы латинского "
                                             "алфавита и цифры от 2 до 7")
    else:
        key = re.sub(r'[\- ]', '', key)
        key += '=' * (-len(key) % 4)
        add_key_to_db(key, user_id, code_number)
        await bot.send_message(user_id, text="Ключ успешно добавлен!")
