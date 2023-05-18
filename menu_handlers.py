from database import check_new_user, get_service_names
from aiogram import types
from aiogram.dispatcher import FSMContext
from bot_utils import bot, UserState, timers
from code_generator import get_code
from bot_messages import INFO_MESSAGE, MAIN_MENU_MESSAGE
from database import get_service_name_from_db


# Функция обработки команды /start
async def handle_start_command(message: types.Message):
    check_new_user(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_button = types.KeyboardButton('Получить меню')
    markup.add(menu_button)
    await message.answer("Нажмите кнопку, чтобы получить меню:", reply_markup=markup)


# Функция обработки нажатия кнопки "Получить меню"
async def handle_menu_button(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton('Получить код', callback_data='get_code_menu'),
        types.InlineKeyboardButton('Ввести ключ', callback_data='enter_key'),
    )
    keyboard.row(
        types.InlineKeyboardButton('Переименовать сервис', callback_data='rename_service')
    )
    keyboard.row(
        types.InlineKeyboardButton('INFO', callback_data='info'),
    )
    await message.answer(
        MAIN_MENU_MESSAGE,
        reply_markup=keyboard
    )


# Функция обработки call`ов отправляемых кнопками inline-меню
async def callback_handler(call: types.CallbackQuery, state: FSMContext):
    user_id = call.message.chat.id
    data = call.data.split(':')
    action = data[0]
    column_number = None
    if len(data) == 2:
        column_number = data[1]

    # Кнопки обработки получения кода для определенного сервиса
    if action == 'get_code':
        await get_code(user_id, column_number, call)

    # Кнопки обработки ввода ключа для определенного сервиса
    elif action == 'set_key':
        await UserState.entering_key.set()
        await state.update_data(column_number=column_number)
        service_name = get_service_name_from_db(user_id, column_number)[0]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('Назад', callback_data='back'))
        await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                    text=f'Введите новый ключ для сервиса "{service_name}":',
                                    parse_mode=types.ParseMode.MARKDOWN,
                                    reply_markup=keyboard)

    # Кнопки обработки изменения имени для определенного сервиса
    elif action == 'rename':
        await UserState.renaming_service.set()
        await state.update_data(column_number=column_number)
        service_name = get_service_name_from_db(user_id, column_number)[0]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('Назад', callback_data='back'))
        await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                    text=f'Введите новое имя для сервиса "{service_name}":',
                                    parse_mode=types.ParseMode.MARKDOWN,
                                    reply_markup=keyboard)

    # Переход в меню изменения имен сервисов
    elif action == 'rename_service':
        await rename_service_menu(user_id, call)

    # Переход в меню получения кодов
    elif action == 'get_code_menu':
        await get_code_menu(user_id, call)

    # Переход в меню ввода ключей
    elif action == 'enter_key':
        await enter_key_menu(user_id, call)

    # Открытие информации
    elif action == 'info':
        await info_menu(user_id, call)

    # Возврат в главное меню
    elif action == 'back':
        await state.reset_state()
        await back_menu(user_id, call)


# Вызов различных меню
# Возврат в главное меню
async def back_menu(user_id, call):
    timer = timers.get(call.message.message_id)
    if timer:
        timer.cancel()
        del timers[call.message.message_id]
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton('Получить код', callback_data='get_code_menu'),
        types.InlineKeyboardButton('Ввести ключ', callback_data='enter_key'),
    )
    keyboard.row(
        types.InlineKeyboardButton('Переименовать сервис', callback_data='rename_service')
    )
    keyboard.row(
        types.InlineKeyboardButton('INFO', callback_data='info'),
    )
    await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text=MAIN_MENU_MESSAGE,
                                parse_mode=types.ParseMode.MARKDOWN,
                                reply_markup=keyboard)


# Информация о боте
async def info_menu(user_id, call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton('Назад', callback_data='back'))
    await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text=INFO_MESSAGE,
                                parse_mode=types.ParseMode.MARKDOWN,
                                reply_markup=keyboard)


# Меню переименовывания сервиса
async def rename_service_menu(user_id, call):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons_row = []
    names = get_service_names(user_id)
    for i, name in enumerate(names):
        buttons_row.append(types.InlineKeyboardButton(name, callback_data=f"rename:{i}"))
    keyboard.add(*buttons_row).add(types.InlineKeyboardButton('Назад', callback_data='back'))
    await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                text='Какой сервис вы бы хотели '
                                     'назвать собственным именем?',
                                reply_markup=keyboard)


# Меню сервисов для получения кодов
async def get_code_menu(user_id, call):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons_row = []
    names = get_service_names(user_id)
    for i, name in enumerate(names):
        buttons_row.append(types.InlineKeyboardButton(name, callback_data=f"get_code:{i}"))
    keyboard.add(*buttons_row).add(types.InlineKeyboardButton('Назад', callback_data='back'))
    await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                text='Для какого сервиса вы хотите '
                                     'получить код?',
                                reply_markup=keyboard)


# Меню сервисов для ввода ключей
async def enter_key_menu(user_id, call):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons_row = []
    names = get_service_names(user_id)
    for i, name in enumerate(names):
        buttons_row.append(types.InlineKeyboardButton(name, callback_data=f"set_key:{i}"))
    keyboard.add(*buttons_row).add(types.InlineKeyboardButton('Назад', callback_data='back'))
    await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                text='Для какого сервиса вы хотите '
                                     'ввести ключ?',
                                reply_markup=keyboard)
