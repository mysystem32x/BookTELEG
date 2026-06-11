from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def admin_menu_keyboard():
  buttons = [
    [KeyboardButton(text="/add_book"), KeyboardButton(text="/delete_book")],
    [KeyboardButton(text="/update_book"), KeyboardButton(text="/create_admin")],
    [KeyboardButton(text="/drop_admin"), KeyboardButton(text="/stats")],
    [KeyboardButton(text="/export"), KeyboardButton(text="/import")],
    [KeyboardButton(text="/users"), KeyboardButton(text="/logs")],
  ]
  return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
