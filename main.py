import os
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web
from dotenv import load_dotenv
from bot import router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def on_startup(bot: Bot):
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

def create_app():
    app = web.Application()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    setup_application(app, dp, bot=bot, path=WEBHOOK_PATH)
    return app

if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=10000)