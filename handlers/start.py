from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.user_keyboards import main_menu_keyboard
from keyboards.admin_keyboards import admin_menu_keyboard
from handlers.survey import start_survey

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, is_admin: bool):
  text = (
    "Ассаламу Алейкум!Я бот-рекомендатор книг.\n\n"
    "Выберите любимые жанры — и я подберу топ-3 книги "
    "с помощью ML-модели.\n\n"
    "Команды:\n"
    "/help - справка\n"
    "/again - новая подборка по тем же предпочтениям\n"
    "/profile - ваши предпочтения\n"
    "/random - случайная рекомендация\n"
    "/history - прочитанные книги\n"
    "/grade - оценить книгу\n\n"
  )

  keyboard = main_menu_keyboard()
  if is_admin:
    await message.answer(text, reply_markup=keyboard)
    await message.answer("🔧 Админ-панель:", reply_markup=admin_menu_keyboard())
  else:
    await message.answer(text, reply_markup=keyboard)

  await start_survey(message, state)


@router.message(Command("help"))
async def cmd_help(message: Message):
  text = (
    "📖 <b>Справка по боту</b>\n\n"
    "<b>/start</b> - начать опрос и получить рекомендации\n"
    "<b>/help</b> - эта справка\n"
    "<b>/again</b> - новая подборка без повторного опроса\n"
    "<b>/profile</b> - посмотреть или изменить предпочтения\n"
    "<b>/random</b> - быстрая рекомендация без опроса\n"
    "<b>/history</b> - список прочитанных книг\n"
    "<b>/grade</b> - оценить книгу от 1 до 5\n\n"
    "Опрос включает выбор жанров из датасета (все уникальные значения столбца «жанр»)."
  )
  await message.answer(text)
