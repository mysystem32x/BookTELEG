from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from config import DATA_DIR
from database.db import get_db
from keyboards.admin_keyboards import users_picker_keyboard
from states.survey_states import AdminStates
from services.book_service import add_book, delete_book, update_book, export_books, import_books
from services.user_service import set_admin, get_stats, get_active_users, create_user

router = Router()


@router.message(Command("add_book"))
async def cmd_add_book(message: Message, state: FSMContext, is_admin: bool):
  if not is_admin:
    await message.answer("⛔ Команда только для администраторов.")
    return
  await state.set_state(AdminStates.add_title)
  await state.update_data(new_book={})
  await message.answer("Введите название книги:")


@router.message(AdminStates.add_title)
async def add_book_title(message: Message, state: FSMContext):
  await state.update_data(new_book={"title": message.text})
  await state.set_state(AdminStates.add_author)
  await message.answer("Введите автора:")


@router.message(AdminStates.add_author)
async def add_book_author(message: Message, state: FSMContext):
  data = await state.get_data()
  book = data["new_book"]
  book["author"] = message.text
  await state.update_data(new_book=book)
  await state.set_state(AdminStates.add_genre)
  await message.answer("Введите жанр:")


@router.message(AdminStates.add_genre)
async def add_book_genre(message: Message, state: FSMContext):
  data = await state.get_data()
  book = data["new_book"]
  book["genre"] = message.text
  await state.update_data(new_book=book)
  await state.set_state(AdminStates.add_mood)
  await message.answer("Введите настроение (веселое/грустное/напряженное):")


@router.message(AdminStates.add_mood)
async def add_book_mood(message: Message, state: FSMContext):
  data = await state.get_data()
  book = data["new_book"]
  book["mood"] = message.text
  await state.update_data(new_book=book)
  await state.set_state(AdminStates.add_description)
  await message.answer("Введите краткое описание:")


@router.message(AdminStates.add_description)
async def add_book_description(message: Message, state: FSMContext):
  data = await state.get_data()
  book = data["new_book"]
  book["description"] = message.text
  await state.update_data(new_book=book)
  await state.set_state(AdminStates.add_rating)
  await message.answer("Введите рейтинг (число от 0 до 5):")


@router.message(AdminStates.add_rating)
async def add_book_rating(message: Message, state: FSMContext):
  data = await state.get_data()
  book = data["new_book"]
  book["rating"] = float(message.text.replace(",", "."))
  await state.update_data(new_book=book)
  await state.set_state(AdminStates.add_pages)
  await message.answer("Введите количество страниц:")


@router.message(AdminStates.add_pages)
async def add_book_pages(message: Message, state: FSMContext):
  data = await state.get_data()
  book = data["new_book"]
  book["pages"] = int(message.text)
  await state.update_data(new_book=book)
  await state.set_state(AdminStates.add_is_new)
  await message.answer("Это новинка? (да/нет):")


@router.message(AdminStates.add_is_new)
async def add_book_is_new(message: Message, state: FSMContext):
  data = await state.get_data()
  book = data["new_book"]
  book["is_new"] = 1 if message.text.lower() in ("да", "yes", "1") else 0
  await state.update_data(new_book=book)
  await state.set_state(AdminStates.add_interests)
  await message.answer("Введите интересы через запятую (или - если нет):")


@router.message(AdminStates.add_interests)
async def add_book_interests(message: Message, state: FSMContext):
  data = await state.get_data()
  book = data["new_book"]
  interests = message.text.strip()
  book["interests"] = "" if interests == "-" else interests

  book_id = await add_book(book)
  await state.clear()
  await message.answer(f"✅ Книга добавлена! ID: {book_id}")


@router.message(Command("delete_book"))
async def cmd_delete_book(message: Message, state: FSMContext, is_admin: bool):
  if not is_admin:
    await message.answer("⛔ Команда только для администраторов.")
    return
  await state.set_state(AdminStates.delete_book_id)
  await message.answer("Введите ID книги для удаления:")


@router.message(AdminStates.delete_book_id)
async def process_delete_book(message: Message, state: FSMContext):
  book_id = int(message.text)
  await delete_book(book_id)
  await state.clear()
  await message.answer(f"✅ Книга ID {book_id} удалена.")


@router.message(Command("update_book"))
async def cmd_update_book(message: Message, state: FSMContext, is_admin: bool):
  if not is_admin:
    await message.answer("⛔ Команда только для администраторов.")
    return
  await state.set_state(AdminStates.update_book_id)
  await message.answer("Введите ID книги для обновления:")


@router.message(AdminStates.update_book_id)
async def process_update_book_id(message: Message, state: FSMContext):
  await state.update_data(book_id=int(message.text))
  await state.set_state(AdminStates.update_field)
  await message.answer(
    "Какое поле обновить?\n"
    "title, author, genre, mood, description, rating, pages, is_new, interests"
  )


@router.message(AdminStates.update_field)
async def process_update_field(message: Message, state: FSMContext):
  await state.update_data(field=message.text.strip())
  await state.set_state(AdminStates.update_value)
  await message.answer("Введите новое значение:")


@router.message(AdminStates.update_value)
async def process_update_value(message: Message, state: FSMContext):
  data = await state.get_data()
  book_id = data["book_id"]
  field = data["field"]
  value = message.text

  if field in ("rating",):
    value = float(value.replace(",", "."))
  elif field in ("pages", "is_new"):
    value = int(value)

  success = await update_book(book_id, field, value)
  await state.clear()

  if success:
    await message.answer(f"✅ Книга ID {book_id} обновлена.")
  else:
    await message.answer("❌ Не удалось обновить. Проверьте поле.")


@router.message(Command("create_admin"))
async def cmd_create_admin(message: Message, is_admin: bool):
  if not is_admin:
    await message.answer("⛔ Команда только для администраторов.")
    return

  users = await get_active_users()
  candidates = [user for user in users if not user["is_admin"]]
  if not candidates:
    await message.answer("Нет пользователей, которых можно назначить администратором.")
    return

  await message.answer(
    "👤 Выберите пользователя для назначения администратором:",
    reply_markup=users_picker_keyboard(candidates[:30], "create"),
  )


@router.message(Command("drop_admin"))
async def cmd_drop_admin(message: Message, is_admin: bool):
  if not is_admin:
    await message.answer("⛔ Команда только для администраторов.")
    return

  users = await get_active_users()
  candidates = [
    user for user in users
    if user["is_admin"] and user["user_id"] != message.from_user.id
  ]
  if not candidates:
    await message.answer("Нет других администраторов для снятия прав.")
    return

  await message.answer(
    "👤 Выберите администратора для снятия прав:",
    reply_markup=users_picker_keyboard(candidates[:30], "drop"),
  )


@router.callback_query(F.data.startswith("admin_user:"))
async def process_admin_user_pick(callback: CallbackQuery, is_admin: bool):
  if not is_admin:
    await callback.answer("⛔ Только для администраторов.", show_alert=True)
    return

  parts = callback.data.split(":")
  if len(parts) != 3:
    await callback.answer()
    return

  action = parts[1]
  if action == "cancel":
    await callback.message.edit_text("❌ Действие отменено.")
    await callback.answer()
    return

  user_id = int(parts[2])

  if action == "create":
    await create_user(user_id, None, is_admin=True)
    await set_admin(user_id, True)
    await callback.message.edit_text(f"✅ Пользователь {user_id} назначен администратором.")
  elif action == "drop":
    await set_admin(user_id, False)
    await callback.message.edit_text(f"✅ Права администратора сняты с {user_id}.")
  else:
    await callback.answer()
    return

  await callback.answer()


@router.message(Command("stats"))
async def cmd_stats(message: Message, is_admin: bool):
  if not is_admin:
    await message.answer("⛔ Команда только для администраторов.")
    return

  stats = await get_stats()
  text = (
    "📊 <b>Статистика бота</b>\n\n"
    f"Пользователей: {stats['users']}\n"
    f"Книг в базе: {stats['books']}\n"
    f"Заполненных профилей: {stats['preferences']}\n"
    f"Записей в истории: {stats['history']}\n"
    f"Оценок: {stats['grades']}\n"
    f"Ошибок в логах: {stats['errors']}"
  )
  await message.answer(text)


@router.message(Command("export"))
async def cmd_export(message: Message, is_admin: bool):
  if not is_admin:
    await message.answer("⛔ Команда только для администраторов.")
    return

  json_path = DATA_DIR / "books_export.json"
  csv_path = DATA_DIR / "books_export.csv"
  json_count = await export_books(json_path, "json")
  csv_count = await export_books(csv_path, "csv")

  await message.answer_document(FSInputFile(json_path), caption=f"JSON: {json_count} книг")
  await message.answer_document(FSInputFile(csv_path), caption=f"CSV: {csv_count} книг")


@router.message(Command("import"))
async def cmd_import(message: Message, state: FSMContext, is_admin: bool):
  if not is_admin:
    await message.answer("⛔ Команда только для администраторов.")
    return
  await state.set_state(AdminStates.import_file)
  await message.answer("Отправьте файл JSON, CSV или XLSX с книгами:")


@router.message(AdminStates.import_file, F.document)
async def process_import_file(message: Message, state: FSMContext):
  file = await message.bot.get_file(message.document.file_id)
  file_path = DATA_DIR / message.document.file_name
  await message.bot.download_file(file.file_path, file_path)

  count = await import_books(file_path)
  await state.clear()
  await message.answer(f"✅ Импортировано книг: {count}")


@router.message(Command("users"))
async def cmd_users(message: Message, is_admin: bool):
  if not is_admin:
    await message.answer("⛔ Команда только для администраторов.")
    return

  users = await get_active_users()
  if not users:
    await message.answer("Пользователей пока нет.")
    return

  lines = ["👥 <b>Активные пользователи:</b>\n"]
  for user in users[:30]:
    admin_mark = " [админ]" if user["is_admin"] else ""
    name = user["username"] or "без username"
    lines.append(
      f"• ID {user['user_id']} (@{name}){admin_mark} — прочитано: {user['books_read']}"
    )

  await message.answer("\n".join(lines))


@router.message(Command("logs"))
async def cmd_logs(message: Message, is_admin: bool):
  if not is_admin:
    await message.answer("⛔ Команда только для администраторов.")
    return

  async with get_db() as db:
    db.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
    cursor = await db.execute(
      "SELECT id, user_id, error_text, created_at FROM error_logs ORDER BY id DESC LIMIT 10"
    )
    logs = await cursor.fetchall()

  if not logs:
    await message.answer("Логов ошибок нет.")
    return

  for log in logs:
    text = (
      f"🚨 <b>Ошибка #{log['id']}</b>\n"
      f"Пользователь: {log['user_id']}\n"
      f"Время: {log['created_at']}\n"
      f"<code>{log['error_text'][:500]}</code>"
    )
    await message.answer(text)
