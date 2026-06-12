from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import MOOD_LABELS, RATING_PREFERENCES, BOOK_LENGTHS
from keyboards.user_keyboards import genres_keyboard, mood_keyboard, rating_keyboard, length_keyboard
from services.genre_service import get_genres
from states.survey_states import SurveyStates
from services.user_service import save_preferences
from handlers.recommendations import send_recommendations

router = Router()


async def start_survey(message: Message, state: FSMContext):
  genres = get_genres()
  if not genres:
    await message.answer("❌ Не удалось загрузить жанры из датасета. Проверьте файл dataset/books.xlsx")
    return

  await state.set_state(SurveyStates.genres)
  await state.update_data(genres=[], page=0)
  await message.answer(
    f"📚 Выберите жанры из датасета ({len(genres)} шт.).\n"
    "Нажмите на жанр, листайте страницы и нажмите «Готово»:",
    reply_markup=genres_keyboard([], page=0),
  )


@router.callback_query(SurveyStates.genres, F.data.startswith("genre:"))
async def process_genres(callback: CallbackQuery, state: FSMContext):
  action = callback.data.split(":", 1)[1]
  data = await state.get_data()
  selected = data.get("genres", [])
  page = data.get("page", 0)
  all_genres = get_genres()

  if action == "noop":
    await callback.answer()
    return

  if action == "done":
    if not selected:
      await callback.answer("Выберите хотя бы один жанр!", show_alert=True)
      return
    await state.set_state(SurveyStates.mood)
    await callback.message.edit_text("✅ Жанры сохранены")
    await callback.message.answer(
      "Какое настроение книги вам ближе?",
      reply_markup=mood_keyboard(),
    )
    await callback.answer()
    return

  if action.startswith("page:"):
    page = int(action.split(":", 1)[1])
    await state.update_data(page=page)
    await callback.message.edit_reply_markup(reply_markup=genres_keyboard(selected, page))
    await callback.answer()
    return

  genre = all_genres[int(action)]
  if genre in selected:
    selected.remove(genre)
  else:
    selected.append(genre)

  await state.update_data(genres=selected)
  await callback.message.edit_reply_markup(reply_markup=genres_keyboard(selected, page))
  await callback.answer()


@router.callback_query(SurveyStates.mood, F.data.startswith("mood:"))
async def process_mood(callback: CallbackQuery, state: FSMContext):
  mood = callback.data.split(":", 1)[1]
  await state.update_data(mood=mood)
  await state.set_state(SurveyStates.rating)
  mood_label = MOOD_LABELS.get(mood, mood)
  await callback.message.edit_text(f"✅ Настроение: {mood_label}")
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
  rating_label = RATING_PREFERENCES.get(rating_pref, rating_pref)
  await callback.message.edit_text(f"✅ Рейтинг: {rating_label}")
  await callback.message.answer(
    "📏 Какой объём книги предпочитаете?",
    reply_markup=length_keyboard(),
  )
  await callback.answer()


@router.callback_query(SurveyStates.length, F.data.startswith("length:"))
async def process_length(callback: CallbackQuery, state: FSMContext):
  book_length = callback.data.split(":", 1)[1]
  data = await state.get_data()
  length_label = BOOK_LENGTHS.get(book_length, book_length)

  await state.set_state(None)
  preferences = {
    "genres": data.get("genres", []),
    "mood": data.get("mood", ""),
    "rating_pref": data.get("rating_pref", "any"),
    "book_length": book_length,
  }
  await save_preferences(callback.from_user.id, **preferences)
  await callback.message.edit_text(f"✅ Объём: {length_label}\n\n✅ Опрос завершён! Подбираю книги...")
  await send_recommendations(callback.message, callback.from_user.id)
  await callback.answer()
