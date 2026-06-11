from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.user_keyboards import (
  genres_keyboard,
  mood_keyboard,
  rating_keyboard,
  length_keyboard,
  interests_keyboard,
)
from states.survey_states import SurveyStates
from services.user_service import save_preferences
from handlers.recommendations import send_recommendations

router = Router()


async def start_survey(message: Message, state: FSMContext):
  await state.set_state(SurveyStates.genres)
  await state.update_data(genres=[], interests=[])
  await message.answer(
    "📚 Выберите любимые жанры (нажмите на жанр, затем «Готово»):",
    reply_markup=genres_keyboard([]),
  )


@router.callback_query(SurveyStates.genres, F.data.startswith("genre:"))
async def process_genres(callback: CallbackQuery, state: FSMContext):
  action = callback.data.split(":", 1)[1]
  data = await state.get_data()
  genres = data.get("genres", [])

  if action == "done":
    if not genres:
      await callback.answer("Выберите хотя бы один жанр!", show_alert=True)
      return
    await state.set_state(SurveyStates.mood)
    await callback.message.edit_text("Какое настроение книги вам ближе?")
    await callback.message.answer("Выберите настроение:", reply_markup=mood_keyboard())
    await callback.answer()
    return

  if action in genres:
    genres.remove(action)
  else:
    genres.append(action)

  await state.update_data(genres=genres)
  await callback.message.edit_reply_markup(reply_markup=genres_keyboard(genres))
  await callback.answer()


@router.callback_query(SurveyStates.mood, F.data.startswith("mood:"))
async def process_mood(callback: CallbackQuery, state: FSMContext):
  mood = callback.data.split(":", 1)[1]
  await state.update_data(mood=mood)
  await state.set_state(SurveyStates.rating)
  await callback.message.edit_text(f"✅ Настроение: {mood}")
  await callback.message.answer(
    "⭐ Насколько важен рейтинг книги?",
    reply_markup=rating_keyboard(),
  )
  await callback.answer()


@router.callback_query(SurveyStates.rating, F.data.startswith("rating:"))
async def process_rating(callback: CallbackQuery, state: FSMContext):
  rating_pref = callback.data.split(":", 1)[1]
  await state.update_data(rating_pref=rating_pref)
  await state.set_state(SurveyStates.length)
  await callback.message.edit_text("✅ Рейтинг учтён")
  await callback.message.answer(
    "📏 Какой объём книги предпочитаете?",
    reply_markup=length_keyboard(),
  )
  await callback.answer()


@router.callback_query(SurveyStates.length, F.data.startswith("length:"))
async def process_length(callback: CallbackQuery, state: FSMContext):
  book_length = callback.data.split(":", 1)[1]
  await state.update_data(book_length=book_length)
  await state.set_state(SurveyStates.interests)
  await callback.message.edit_text("✅ Объём учтён")
  await callback.message.answer(
    "🎯 Выберите интересы (можно несколько, затем «Готово»):",
    reply_markup=interests_keyboard([]),
  )
  await callback.answer()


@router.callback_query(SurveyStates.interests, F.data.startswith("interest:"))
async def process_interests(callback: CallbackQuery, state: FSMContext):
  action = callback.data.split(":", 1)[1]
  data = await state.get_data()
  interests = data.get("interests", [])

  if action == "done":
    await state.set_state(None)
    preferences = {
      "genres": data.get("genres", []),
      "mood": data.get("mood", ""),
      "rating_pref": data.get("rating_pref", "any"),
      "book_length": data.get("book_length", "medium"),
      "interests": interests,
    }
    await save_preferences(callback.from_user.id, **preferences)
    await callback.message.edit_text("✅ Опрос завершён! Подбираю книги...")
    await send_recommendations(callback.message, callback.from_user.id)
    await callback.answer()
    return

  if action in interests:
    interests.remove(action)
  else:
    interests.append(action)

  await state.update_data(interests=interests)
  await callback.message.edit_reply_markup(reply_markup=interests_keyboard(interests))
  await callback.answer()
