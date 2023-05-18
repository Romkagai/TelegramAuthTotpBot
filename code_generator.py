import pyotp
import datetime
import asyncio
from database import get_key_from_db, get_service_name_from_db
from aiogram import types
from bot_utils import bot, timers
from bot_messages import NO_KEY_MESSAGE, CODE_EXPIRED_MESSAGE


# Функция генерации totp-кода
async def generate_totp(key):
    totp = pyotp.TOTP(key)
    code = totp.now()
    remaining_time = totp.interval - (datetime.datetime.now().timestamp() % totp.interval)
    return code, remaining_time


# Функция получения кода
async def get_code(user_id, code_number, call):
    markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton(text='Назад', callback_data='back')
    markup.row(back_btn)
    key = get_key_from_db(user_id, code_number)[0]
    if key is None:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=NO_KEY_MESSAGE
                                    , reply_markup=markup)
        return
    service_name = get_service_name_from_db(user_id, code_number)[0]
    code, remaining_time = await generate_totp(key)
    await update_message_loop(call.message.chat.id, call.message.message_id, remaining_time, code, service_name, markup,
                              code_number)


# Функция обновления сообщения с кодом
async def update_message_loop(chat_id, message_id, remaining_time, totp_code, service_name, markup, code_number):
    start_time = asyncio.get_running_loop().time()
    if remaining_time <= 0:
        if message_id in timers:
            timers[message_id].cancel()
            del timers[message_id]
        refresh_btn = types.InlineKeyboardButton(text='Получить новый код',
                                                 callback_data=f'get_code:{code_number}')
        markup.row(refresh_btn)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=CODE_EXPIRED_MESSAGE,
                                    reply_markup=markup)
        return
    time_bar = await get_time_bar(remaining_time, 30)
    new_text = f"Код для входа в {service_name}:<pre>{totp_code}</pre>(Нажмите, чтобы скопировать)\n\nВремя действия: "\
               f"{await format_time(remaining_time)}\n{time_bar} "
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, reply_markup=markup,
                                parse_mode="HTML")
    elapsed_time = asyncio.get_running_loop().time() - start_time
    wait_time = max(1 - elapsed_time, 0)
    await asyncio.sleep(wait_time)
    timers[message_id] = asyncio.create_task(
        update_message_loop(chat_id, message_id, remaining_time - 1, totp_code, service_name, markup, code_number))


# Вспомогательная функция: генерирует строку эмодзи для визуального отображения времени
async def get_time_bar(seconds_left, total_seconds):
    bar = "🟩" * int(seconds_left / total_seconds * 15)
    bar += "🟥" * (15 - len(bar))
    return f"{bar}"


# Вспомогательная функция: форматирует время для корректного отображения
async def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    return "{:02d}:{:02d}".format(int(minutes), int(seconds))
