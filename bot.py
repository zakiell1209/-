import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "ВАШ_ТОКЕН_ТЕЛЕГРАМ"
REPLICATE_API_TOKEN = "ВАШ_ТОКЕН_REPLICATE"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

HEADERS = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json"
}

user_states = {}

def get_model_selection_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("SFW (без NSFW)", callback_data="model_sfw"),
        InlineKeyboardButton("NSFW (взрослый контент)", callback_data="model_nsfw"),
    )
    kb.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
    return kb

MODELS = {
    "model_sfw": "a9758cb7b56e3353f62b041616f36a33b7f17774b491652b810d3f738a5a9f25",  # пример SFW модели
    "model_nsfw": "dcb8bb7a2d1a1a1b3f2439e28c5f4e31bb03153c8a9eb4ee3d00a4ec7f4781c0"   # пример NSFW модели
}

STATE_WAITING_DESCRIPTION = "waiting_description"

@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Выбери тип генерации изображения:",
        reply_markup=get_model_selection_keyboard()
    )
    user_states.pop(message.from_user.id, None)

@dp.callback_query_handler(lambda c: c.data in ["model_sfw", "model_nsfw", "cancel"])
async def process_model_selection(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data == "cancel":
        user_states.pop(user_id, None)
        await callback_query.message.edit_text("Отменено. Введите /start для выбора модели.")
        await callback_query.answer()
        return

    user_states[user_id] = {
        "model": MODELS[data],
        "state": STATE_WAITING_DESCRIPTION
    }
    await callback_query.message.edit_text("Отлично! Теперь отправьте описание для генерации изображения.")
    await callback_query.answer()

@dp.message_handler()
async def process_description(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_states or user_states[user_id].get("state") != STATE_WAITING_DESCRIPTION:
        await message.answer("Пожалуйста, сначала выберите модель через команду /start.")
        return

    prompt = message.text.strip()
    if not prompt:
        await message.reply("Описание не может быть пустым.")
        return

    model_version = user_states[user_id]["model"]
    await message.answer("Генерирую изображение, подождите...")

    prediction_id = await create_prediction(prompt, model_version)
    if not prediction_id:
        await message.answer("Ошибка создания задачи генерации.")
        return

    image_url = await wait_for_result(prediction_id)
    if not image_url:
        await message.answer("Не удалось получить результат.")
        return

    await message.answer_photo(photo=image_url, caption=f"Ваше изображение по запросу:\n{prompt}")
    user_states.pop(user_id, None)

async def create_prediction(prompt: str, model_version: str) -> str | None:
    json_data = {
        "version": model_version,
        "input": {
            "prompt": prompt,
            "num_outputs": 1,
            "num_inference_steps": 30,
            "guidance_scale": 7.5
        }
    }
    try:
        resp = requests.post("https://api.replicate.com/v1/predictions", headers=HEADERS, json=json_data)
        resp.raise_for_status()
        data = resp.json()
        return data["id"]
    except Exception as e:
        logging.error(f"Error creating prediction: {e}")
        return None

async def wait_for_result(prediction_id: str, timeout: int = 60) -> str | None:
    url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
    for _ in range(timeout // 3):
        try:
            resp = requests.get(url, headers=HEADERS)
            resp.raise_for_status()
            data = resp.json()
            if data["status"] == "succeeded":
                return data["output"][0]
            elif data["status"] == "failed":
                logging.error(f"Prediction failed: {data}")
                return None
        except Exception as e:
            logging.error(f"Error checking prediction status: {e}")
            return None
        await asyncio.sleep(3)
    return None

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)