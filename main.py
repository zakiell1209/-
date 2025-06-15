import os
from fastapi import FastAPI, Request
from aiogram import Bot
from aiogram.fsm.storage.memory import MemoryStorage
from bot import dp, bot
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f"/webhook/{os.getenv('BOT_TOKEN')}"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    body = await request.body()
    await dp.feed_raw_update(bot=bot, update=body)
    return {"ok": True}