from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("👋 Привет! Я генератор изображений. Отправь описание, и я сгенерирую картинку!")

@router.message()
async def prompt_handler(message: types.Message):
    prompt = message.text
    await message.answer(f"Ты отправил: {prompt}\n(Тут будет генерация через Replicate)")