import os
import logging
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")
REPLICATE_MODEL = "aitechtree/nsfw-novel-generation"

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Отправь описание, и я сгенерирую изображение.")

@dp.message(F.text)
async def generate_image(message: Message):
    prompt = message.text.strip()
    headers = {"Authorization": f"Token {REPLICATE_TOKEN}"}
    json_data = {
        "version": "latest",
        "input": {
            "prompt": prompt
        }
    }
    response = requests.post(
        f"https://api.replicate.com/v1/predictions",
        headers=headers,
        json=json_data,
    )
    if response.status_code != 201:
        await message.answer("Ошибка при генерации.")
        return

    prediction = response.json()
    await message.answer("Генерация началась...")

    # Ожидаем завершения
    prediction_url = prediction["urls"]["get"]
    while True:
        result = requests.get(prediction_url, headers=headers).json()
        status = result["status"]
        if status == "succeeded":
            output_url = result["output"][0] if isinstance(result["output"], list) else result["output"]
            await message.answer_photo(output_url)
            break
        elif status == "failed":
            await message.answer("Ошибка генерации.")
            break

# Для Render — вебхук:
async def on_startup(app):
    await bot.set_webhook(os.getenv("WEBHOOK_URL"))

def create_app():
    app = web.Application()
    app.on_startup.append(on_startup)
    setup_application(app, dp, bot=bot)
    return app

app = create_app()