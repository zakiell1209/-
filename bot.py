 import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.replicate import generate_image
from bot.keyboards import get_model_keyboard

router = Router()

class GenState(StatesGroup):
    waiting_for_prompt = State()
    waiting_for_model = State()

@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.set_state(GenState.waiting_for_prompt)
    await message.answer("👋 Отправь описание для NSFW изображения:")

@router.message(GenState.waiting_for_prompt)
async def ask_model(message: Message, state: FSMContext):
    await state.update_data(prompt=message.text)
    await state.set_state(GenState.waiting_for_model)
    await message.answer("Выбери модель генерации:", reply_markup=get_model_keyboard())

@router.callback_query(GenState.waiting_for_model)
async def generate(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    prompt = data["prompt"]
    model = callback.data
    await callback.message.edit_text("🧠 Генерация изображения…")
    image_url = generate_image(prompt, model)
    await callback.message.answer_photo(photo=image_url)
    await state.clear()