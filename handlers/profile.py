from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.user_keyboards import profile_keyboard
from services.user_service import get_preferences
from utils.messages import format_preferences
from handlers.survey import start_survey

router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message):
  preferences = await get_preferences(message.from_user.id)
  text = format_preferences(preferences)
  await message.answer(text, reply_markup=profile_keyboard())


@router.callback_query(F.data == "profile:edit")
async def edit_profile(callback: CallbackQuery, state: FSMContext):
  await callback.message.answer("Начинаем новый опрос для обновления предпочтений:")
  await start_survey(callback.message, state)
  await callback.answer()
