from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot_token import token
import logging

# Устанавливаем уровень логов на INFO
logging.basicConfig(level=logging.INFO)

# Объекты бота и диспетчера
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Машина состояний пользователя (обработка текстовых сообщений)
class UserState(StatesGroup):
    entering_key = State()
    renaming_service = State()


# В этом словаре в дальнейшем храним таймеры (нужны для корректного отображения времени для каждого пользователя)
timers = {}
