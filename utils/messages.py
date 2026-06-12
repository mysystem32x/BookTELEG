from config import MOOD_LABELS, RATING_PREFERENCES, BOOK_LENGTHS


def format_book_recommendation(number, book, reason):
  text = (
    f"📚 <b>Рекомендация #{number}</b>\n\n"
    f"<b>{book['title']}</b>\n"
    f"Автор: {book['author']}\n"
    f"Жанр: {book['genre']}\n"
    f"Рейтинг: {book['rating']} ⭐\n"
    f"Страниц: {book['pages']}\n\n"
    f"📝 {book['description']}\n\n"
    f"💡 {reason}"
  )
  return text


def format_preferences(preferences):
  if not preferences:
    return "Предпочтения ещё не заполнены. Пройдите опрос через /start"

  genres = ", ".join(preferences["genres"]) if preferences["genres"] else "не выбраны"
  mood = MOOD_LABELS.get(preferences["mood"], preferences["mood"] or "не выбрано")
  rating_text = RATING_PREFERENCES.get(preferences["rating_pref"], preferences["rating_pref"])
  length_text = BOOK_LENGTHS.get(preferences["book_length"], preferences["book_length"])

  return (
    "👤 <b>Ваши предпочтения:</b>\n\n"
    f"Жанры: {genres}\n"
    f"Настроение: {mood}\n"
    f"Рейтинг: {rating_text}\n"
    f"Объём: {length_text}"
  )
