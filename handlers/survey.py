from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.user_keyboards import genres_keyboard
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
    await state.set_state(None)
    await save_preferences(callback.from_user.id, genres=selected)
    await callback.message.edit_text("✅ Опрос завершён! Подбираю книги...")
    await send_recommendations(callback.message, callback.from_user.id)
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
