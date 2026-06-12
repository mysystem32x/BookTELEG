from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.recommender import get_recommendations
from services.user_service import get_preferences
from utils.messages import format_book_recommendation

router = Router()


async def send_recommendations(message: Message, user_id: int, random_mode=False):
  preferences = await get_preferences(user_id)
  recommendations = await get_recommendations(preferences, count=3, random_mode=random_mode)

  if not recommendations:
    if random_mode:
      await message.answer("😔 В базе пока нет книг.")
    elif preferences and preferences.get("genres"):
      genres = ", ".join(preferences["genres"])
      await message.answer(f"😔 По жанрам «{genres}» книг в базе пока нет.")
    else:
      await message.answer(
        "😔 Не удалось подобрать книги. Пройдите опрос через /start"
      )
    return

  mode = recommendations[0].get("mode", "combined")
  if mode == "per_genre":
    await message.answer(
      "🎯 <b>Точных совпадений не нашлось — подборка отдельно по каждому жанру:</b>"
    )
  else:
    await message.answer("🎯 <b>Ваши рекомендации (топ-3):</b>")

  for index, item in enumerate(recommendations, start=1):
    text = format_book_recommendation(index, item["book"], item["reason"])
    if mode == "per_genre" and item.get("genre"):
      text = f"📂 <b>Жанр: {item['genre']}</b>\n\n{text}"
    await message.answer(text)


@router.message(Command("again"))
async def cmd_again(message: Message):
  preferences = await get_preferences(message.from_user.id)
  if not preferences:
    await message.answer("Сначала пройдите опрос через /start")
    return

  await message.answer("🔄 Подбираю новую подборку...")
  await send_recommendations(message, message.from_user.id)


@router.message(Command("random"))
async def cmd_random(message: Message):
  await message.answer("🎲 Случайная рекомендация...")
  await send_recommendations(message, message.from_user.id, random_mode=True)
