import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import BOOK_LENGTHS
from services.book_service import get_all_books
from services.genre_service import genre_matches, matched_genres


async def get_recommendations(preferences, count=3, random_mode=False):
  """Подбирает книги: случайно или по ML-сходству текстовых профилей."""
  books = await get_all_books()
  if not books:
    return []

  if random_mode:
    selected = random.sample(books, min(count, len(books)))
    return [
      {
        "book": book,
        "reason": "Случайная рекомендация — попробуйте что-то новое!",
        "mode": "random",
      }
      for book in selected
    ]

  if not preferences:
    return []

  user_genres = preferences.get("genres", [])
  scores = _score_books(preferences, books)

  matching = [
    (book, scores[index])
    for index, book in enumerate(books)
    if _passes_filters(book, preferences)
  ]

  if matching:
    matching.sort(key=lambda pair: pair[1], reverse=True)
    return [
      {
        "book": book,
        "reason": _build_reason(book, preferences, score),
        "mode": "combined",
      }
      for book, score in matching[:count]
    ]

  if not user_genres:
    return []

  return _get_per_genre_recommendations(books, scores, preferences, user_genres, count)


def _score_books(preferences, books):
  user_text = _build_user_text(preferences)
  book_texts = [_build_book_text(book) for book in books]

  vectorizer = TfidfVectorizer()
  matrix = vectorizer.fit_transform([user_text] + book_texts)
  return cosine_similarity(matrix[0:1], matrix[1:])[0]


def _get_per_genre_recommendations(books, scores, preferences, user_genres, count):
  result = []
  used_ids = set()

  for genre in user_genres:
    if len(result) >= count:
      break

    genre_matches_list = [
      (book, scores[index])
      for index, book in enumerate(books)
      if book["id"] not in used_ids and genre_matches(book["genre"], [genre])
    ]
    if not genre_matches_list:
      continue

    genre_matches_list.sort(key=lambda pair: pair[1], reverse=True)
    book, score = genre_matches_list[0]
    used_ids.add(book["id"])

    single_prefs = {**preferences, "genres": [genre]}
    result.append({
      "book": book,
      "reason": _build_reason(
        book,
        single_prefs,
        score,
        fallback_genre=genre,
      ),
      "mode": "per_genre",
      "genre": genre,
    })

  return result


def _build_user_text(preferences):
  parts = []
  parts.extend(preferences.get("genres", []))
  parts.append(preferences.get("mood", ""))
  parts.extend(preferences.get("interests", []))
  parts.append(preferences.get("book_length", ""))
  parts.append(preferences.get("rating_pref", ""))
  return " ".join(parts)


def _build_book_text(book):
  parts = [
    book["genre"],
    book["mood"],
    book["description"],
    book.get("interests", ""),
    str(book.get("pages", "")),
  ]
  return " ".join(parts)


def _passes_filters(book, preferences):
  genres = preferences.get("genres", [])
  if genres and not genre_matches(book["genre"], genres):
    return False

  mood = preferences.get("mood", "")
  if mood and book["mood"] != mood:
    return False

  rating_pref = preferences.get("rating_pref", "any")
  if rating_pref == "hits" and book["rating"] < 4.0:
    return False

  length = preferences.get("book_length", "medium")
  pages = book.get("pages", 300)

  if length == "short" and pages > 200:
    return False
  if length == "medium" and (pages < 200 or pages > 400):
    return False
  if length == "long" and pages < 400:
    return False

  return True


def _build_reason(book, preferences, score, fallback_genre=None):
  reasons = []

  if fallback_genre:
    reasons.append(f"лучшая книга по жанру «{fallback_genre}»")
  else:
    genres = preferences.get("genres", [])
    common_genres = matched_genres(book["genre"], genres)
    if common_genres:
      reasons.append(f"жанр «{', '.join(common_genres)}» в вашем списке любимых")

  mood = preferences.get("mood", "")
  if mood and book["mood"] == mood:
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

  if not reasons:
    match_percent = int(score * 100)
    reasons.append(f"совпадение с вашими предпочтениями ~{match_percent}%")

  return "Подходит потому что: " + "; ".join(reasons) + "."
