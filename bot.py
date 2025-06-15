import logging
from aiogram import Bot, Dispatcher, executor, types
import os

API_TOKEN = os.getenv("TELEGRAM_TOKEN")  # твой токен в env

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я готов принимать команды.")


@dp.message_handler(commands=["help"])
async def send_help(message: types.Message):
    await message.reply("Это простой бот на aiogram 2.")


@dp.message_handler()
async def echo(message: types.Message):
    # Просто повторяем сообщение назад
    await message.answer(message.text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)