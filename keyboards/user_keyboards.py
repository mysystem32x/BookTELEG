from aiogram.types import (
  ReplyKeyboardMarkup,
  KeyboardButton,
  InlineKeyboardMarkup,
  InlineKeyboardButton,
)

from config import GENRES, MOODS, RATING_PREFERENCES, BOOK_LENGTHS, INTERESTS


def main_menu_keyboard():
  buttons = [
    [KeyboardButton(text="/start"), KeyboardButton(text="/help")],
    [KeyboardButton(text="/again"), KeyboardButton(text="/profile")],
    [KeyboardButton(text="/random"), KeyboardButton(text="/history")],
    [KeyboardButton(text="/grade")],
  ]
  return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def genres_keyboard(selected_genres):
  buttons = []
  row = []
  for genre in GENRES:
    mark = "✅ " if genre in selected_genres else ""
    row.append(InlineKeyboardButton(text=f"{mark}{genre}", callback_data=f"genre:{genre}"))
    if len(row) == 2:
      buttons.append(row)
      row = []
  if row:
    buttons.append(row)
  buttons.append([InlineKeyboardButton(text="✅ Готово", callback_data="genre:done")])
  return InlineKeyboardMarkup(inline_keyboard=buttons)


def mood_keyboard():
  buttons = [[InlineKeyboardButton(text=mood, callback_data=f"mood:{mood}")] for mood in MOODS]
  return InlineKeyboardMarkup(inline_keyboard=buttons)


def rating_keyboard():
  buttons = [
    [InlineKeyboardButton(text=text, callback_data=f"rating:{key}")]
    for key, text in RATING_PREFERENCES.items()
  ]
  return InlineKeyboardMarkup(inline_keyboard=buttons)


def length_keyboard():
  buttons = [
    [InlineKeyboardButton(text=text, callback_data=f"length:{key}")]
    for key, text in BOOK_LENGTHS.items()
  ]
  return InlineKeyboardMarkup(inline_keyboard=buttons)


def interests_keyboard(selected_interests):
  buttons = []
  row = []
  for interest in INTERESTS:
    mark = "✅ " if interest in selected_interests else ""
    row.append(InlineKeyboardButton(text=f"{mark}{interest}", callback_data=f"interest:{interest}"))
    if len(row) == 2:
      buttons.append(row)
      row = []
  if row:
    buttons.append(row)
  buttons.append([InlineKeyboardButton(text="✅ Готово", callback_data="interest:done")])
  return InlineKeyboardMarkup(inline_keyboard=buttons)


def grade_keyboard(book_id):
  buttons = [
    [
      InlineKeyboardButton(text=str(i), callback_data=f"grade:{book_id}:{i}")
      for i in range(1, 6)
    ]
  ]
  return InlineKeyboardMarkup(inline_keyboard=buttons)


def profile_keyboard():
  buttons = [
    [InlineKeyboardButton(text="Изменить предпочтения", callback_data="profile:edit")],
  ]
  return InlineKeyboardMarkup(inline_keyboard=buttons)
