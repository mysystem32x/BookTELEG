from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.user_service import get_read_history, add_to_history
from services.book_service import get_book_by_id

router = Router()


@router.message(Command("history"))
async def cmd_history(message: Message):
  history = await get_read_history(message.from_user.id)

  if not history:
    await message.answer("📭 Вы ещё не отмечали прочитанные книги.")
    return

  lines = ["📚 <b>Прочитанные книги:</b>\n"]
  for item in history:
    lines.append(f"• <b>{item['title']}</b> — {item['author']} ({item['read_at'][:10]})")

  await message.answer("\n".join(lines))


async def mark_book_as_read(user_id, book_id):
  book = await get_book_by_id(book_id)
  if book:
    await add_to_history(user_id, book_id)
