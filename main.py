import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import setup_routers
from middlewares import AdminMiddleware, ErrorMiddleware
from services.book_service import seed_books_from_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
  if not BOT_TOKEN:
    logger.error("Укажите BOT_TOKEN в файле .env")
    return

  await init_db()
  await seed_books_from_dataset()

  bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
  dp = Dispatcher(storage=MemoryStorage())

  dp.update.middleware(AdminMiddleware())
  dp.update.middleware(ErrorMiddleware())
  dp.include_router(setup_routers())

  logger.info("Бот запущен")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
