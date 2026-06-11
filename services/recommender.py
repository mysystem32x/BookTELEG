import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import BOOK_LENGTHS
from services.book_service import get_all_books


async def get_recommendations(preferences, count=3, random_mode=False):
  """Подбирает книги: случайно или по ML-сходству текстовых профилей."""
  books = await get_all_books()
  if not books:
    return []

  # Режим /random — без ML, просто случайный выбор из каталога
  if random_mode:
    selected = random.sample(books, min(count, len(books)))
    result = []
    for book in selected:
      result.append({
        "book": book,
        "reason": "Случайная рекомендация — попробуйте что-то новое!",
      })
    return result

  if not preferences:
    return []

  # Собираем текстовые описания пользователя и всех книг
  user_text = _build_user_text(preferences)
  book_texts = [_build_book_text(book) for book in books]

  # TF-IDF: превращаем тексты в числовые векторы по важности слов
  vectorizer = TfidfVectorizer()
  all_texts = [user_text] + book_texts
  matrix = vectorizer.fit_transform(all_texts)

  # Первая строка — профиль пользователя, остальные — книги
  user_vector = matrix[0:1]
  book_vectors = matrix[1:]
  # Косинусное сходство: чем ближе к 1, тем больше совпадение
  scores = cosine_similarity(user_vector, book_vectors)[0]

  # Оставляем только книги, прошедшие жёсткие фильтры (жанр, настроение, объём…)
  filtered_books = []
  filtered_scores = []

  for index, book in enumerate(books):
    if not _passes_filters(book, preferences):
      continue
    filtered_books.append(book)
    filtered_scores.append(scores[index])

  # Если фильтры отсеяли всё — берём топ по ML без фильтров
  if not filtered_books:
    top_indexes = scores.argsort()[::-1][:count]
    filtered_books = [books[i] for i in top_indexes]
    filtered_scores = [scores[i] for i in top_indexes]
  else:
    # Сортируем отфильтрованные книги по убыванию сходства
    sorted_pairs = sorted(zip(filtered_books, filtered_scores), key=lambda x: x[1], reverse=True)
    filtered_books = [pair[0] for pair in sorted_pairs[:count]]
    filtered_scores = [pair[1] for pair in sorted_pairs[:count]]

  # Формируем ответ: книга + человекочитаемое объяснение
  result = []
  for book, score in zip(filtered_books, filtered_scores):
    reason = _build_reason(book, preferences, score)
    result.append({"book": book, "reason": reason})

  return result


def _build_user_text(preferences):
  """Склеивает ответы опроса в одну строку для векторизации."""
  parts = []
  parts.extend(preferences.get("genres", []))
  parts.append(preferences.get("mood", ""))
  parts.extend(preferences.get("interests", []))
  parts.append(preferences.get("book_length", ""))
  parts.append(preferences.get("rating_pref", ""))
  return " ".join(parts)


def _build_book_text(book):
  """Склеивает поля книги в одну строку для сравнения с профилем пользователя."""
  parts = [
    book["genre"],
    book["mood"],
    book["description"],
    book.get("interests", ""),
    str(book.get("pages", "")),
  ]
  return " ".join(parts)


def _genre_matches(book_genre, user_genres):
  """Проверяет, входит ли жанр пользователя в строку жанров книги."""
  book_lower = book_genre.lower()
  for genre in user_genres:
    if genre.lower() in book_lower:
      return True
  return False


def _passes_filters(book, preferences):
  """Жёсткие правила: книга отбрасывается, если не подходит по критериям опроса."""
  genres = preferences.get("genres", [])
  if genres and not _genre_matches(book["genre"], genres):
    return False

  mood = preferences.get("mood", "")
  if mood and book["mood"] != mood:
    return False

  rating_pref = preferences.get("rating_pref", "any")
  if rating_pref == "hits" and book["rating"] < 4.0:
    return False

  if rating_pref == "any" and preferences.get("prefer_new"):
    pass

  length = preferences.get("book_length", "medium")
  pages = book.get("pages", 300)

  if length == "short" and pages > 200:
    return False
  if length == "medium" and (pages < 200 or pages > 400):
    return False
  if length == "long" and pages < 400:
    return False

  return True


def _build_reason(book, preferences, score):
  """Собирает текст «почему подходит» из совпавших полей или процента сходства."""
  reasons = []

  genres = preferences.get("genres", [])
  matched_genres = [genre for genre in genres if genre.lower() in book["genre"].lower()]
  if matched_genres:
    reasons.append(f"жанр «{', '.join(matched_genres)}» в вашем списке любимых")

  mood = preferences.get("mood", "")
  if book["mood"] == mood:
    reasons.append(f"настроение «{mood}» совпадает с вашим выбором")

  interests = preferences.get("interests", [])
  book_interests = book.get("interests", "").split(",") if book.get("interests") else []
  common = set(interests) & set(book_interests)
  if common:
    reasons.append(f"общие интересы: {', '.join(common)}")

  length = preferences.get("book_length", "")
  if length:
    reasons.append(f"объём подходит ({BOOK_LENGTHS.get(length, length)})")

  if book["rating"] >= 4.5:
    reasons.append(f"высокий рейтинг ({book['rating']})")

  # Если явных совпадений нет — показываем ML-оценку в процентах
  if not reasons:
    match_percent = int(score * 100)
    reasons.append(f"совпадение с вашими предпочтениями ~{match_percent}%")

  return "Подходит потому что: " + "; ".join(reasons) + "."
