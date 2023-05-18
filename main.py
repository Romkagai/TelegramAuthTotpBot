# Импортируем базовые функции для настройки и запуска бота
from database import create_or_check_database
from bot_utils import dp, UserState
from menu_handlers import callback_handler, handle_start_command, handle_menu_button
from state_handlers import handle_enter_key, handle_rename_service

# Создание и проверка на существование базы данных
create_or_check_database()

# Регистрация хэндлеров
dp.register_message_handler(handle_start_command, commands=['start'])
dp.register_message_handler(handle_menu_button, lambda message: message.text == "Получить меню")
dp.register_callback_query_handler(callback_handler, lambda call: True, state='*')
dp.register_message_handler(handle_enter_key, state=UserState.entering_key)
dp.register_message_handler(handle_rename_service, state=UserState.renaming_service)

# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
