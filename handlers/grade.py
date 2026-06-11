from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.user_keyboards import grade_keyboard
from services.book_service import get_all_books
from services.user_service import save_grade, add_to_history
from states.survey_states import GradeStates

router = Router()


@router.message(Command("grade"))
async def cmd_grade(message: Message, state: FSMContext):
  books = await get_all_books()
  if not books:
    await message.answer("В базе нет книг для оценки.")
    return

  await state.set_state(GradeStates.choose_book)
  lines = ["⭐ Выберите книгу для оценки (введите ID):\n"]
  for book in books[:20]:
    lines.append(f"ID {book['id']}: <b>{book['title']}</b> — {book['author']}")

  if len(books) > 20:
    lines.append(f"\n... и ещё {len(books) - 20} книг")

  await message.answer("\n".join(lines))


@router.message(GradeStates.choose_book)
async def choose_book_for_grade(message: Message, state: FSMContext):
  if not message.text or not message.text.strip().isdigit():
    await message.answer("Введите числовой ID книги из списка.")
    return

  book_id = int(message.text.strip())
  from services.book_service import get_book_by_id
  book = await get_book_by_id(book_id)

  if not book:
    await message.answer("Книга с таким ID не найдена. Попробуйте снова.")
    return

  await state.update_data(book_id=book_id)
  await state.set_state(None)
  await message.answer(
    f"Оцените «{book['title']}» от 1 до 5:",
    reply_markup=grade_keyboard(book_id),
  )


@router.callback_query(F.data.startswith("grade:"))
async def process_grade(callback: CallbackQuery):
  parts = callback.data.split(":")
  book_id = int(parts[1])
  grade = int(parts[2])

  await save_grade(callback.from_user.id, book_id, grade)
  await add_to_history(callback.from_user.id, book_id)

  await callback.message.edit_text(f"✅ Спасибо! Вы поставили оценку {grade}/5")
  await callback.answer()
