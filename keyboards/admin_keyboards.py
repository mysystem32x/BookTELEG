from aiogram.types import (
  ReplyKeyboardMarkup,
  KeyboardButton,
  InlineKeyboardMarkup,
  InlineKeyboardButton,
)


def admin_menu_keyboard():
  buttons = [
    [KeyboardButton(text="/add_book"), KeyboardButton(text="/delete_book")],
    [KeyboardButton(text="/update_book"), KeyboardButton(text="/create_admin")],
    [KeyboardButton(text="/drop_admin"), KeyboardButton(text="/stats")],
    [KeyboardButton(text="/export"), KeyboardButton(text="/import")],
    [KeyboardButton(text="/users"), KeyboardButton(text="/logs")],
  ]
  return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def users_picker_keyboard(users, action):
  buttons = []
  for user in users:
    username = user.get("username")
    label = f"@{username}" if username else f"Пользователь {user['user_id']}"
    if user.get("is_admin"):
      label += " [админ]"
    buttons.append([
      InlineKeyboardButton(
        text=label,
        callback_data=f"admin_user:{action}:{user['user_id']}",
      )
    ])
  buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="admin_user:cancel")])
  return InlineKeyboardMarkup(inline_keyboard=buttons)
