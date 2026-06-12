from aiogram.types import (
  ReplyKeyboardMarkup,
  KeyboardButton,
  KeyboardButtonRequestUsers,
  InlineKeyboardMarkup,
  InlineKeyboardButton,
)

REQUEST_CREATE_ADMIN = 1
REQUEST_DROP_ADMIN = 2


def admin_menu_keyboard():
  buttons = [
    [KeyboardButton(text="/add_book"), KeyboardButton(text="/delete_book")],
    [KeyboardButton(text="/update_book"), KeyboardButton(text="/create_admin")],
    [KeyboardButton(text="/drop_admin"), KeyboardButton(text="/stats")],
    [KeyboardButton(text="/export"), KeyboardButton(text="/import")],
    [KeyboardButton(text="/users"), KeyboardButton(text="/logs")],
  ]
  return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def admin_user_picker_reply_keyboard(action):
  request_id = REQUEST_CREATE_ADMIN if action == "create" else REQUEST_DROP_ADMIN
  return ReplyKeyboardMarkup(
    keyboard=[
      [
        KeyboardButton(
          text="👤 Выбрать пользователя",
          request_users=KeyboardButtonRequestUsers(
            request_id=request_id,
            user_is_bot=False,
            max_quantity=1,
            request_username=True,
          ),
        ),
      ],
      [KeyboardButton(text="❌ Отмена")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
  )


def admins_drop_keyboard(admins):
  buttons = []
  for user in admins:
    username = user.get("username")
    label = f"@{username}" if username else f"Пользователь {user['user_id']}"
    buttons.append([
      InlineKeyboardButton(
        text=label,
        callback_data=f"admin_user:drop:{user['user_id']}",
      )
    ])
  buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="admin_user:cancel")])
  return InlineKeyboardMarkup(inline_keyboard=buttons)
