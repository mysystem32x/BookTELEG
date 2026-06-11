import traceback
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database.db import get_db


class ErrorMiddleware(BaseMiddleware):
  async def __call__(
    self,
    handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
    event: TelegramObject,
    data: Dict[str, Any],
  ):
    try:
      return await handler(event, data)
    except Exception as error:
      user = data.get("event_from_user")
      user_id = user.id if user else None
      error_text = f"{type(error).__name__}: {error}\n{traceback.format_exc()}"

      async with get_db() as db:
        await db.execute(
          "INSERT INTO error_logs (user_id, error_text) VALUES (?, ?)",
          (user_id, error_text),
        )
        await db.commit()

      raise
