import logging
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "ВАШ_ТОКЕН_ТЕЛЕГРАМ"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот на aiogram 2.x, работаю без Rust.")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)