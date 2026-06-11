from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from config import ADMIN_IDS
from services.user_service import get_user, create_user


class AdminMiddleware(BaseMiddleware):
  async def __call__(
    self,
    handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
    event: TelegramObject,
    data: Dict[str, Any],
  ):
    user = data.get("event_from_user")
    if user:
      db_user = await get_user(user.id)
      if not db_user:
        is_admin = user.id in ADMIN_IDS
        await create_user(user.id, user.username, is_admin)
        db_user = await get_user(user.id)
      data["is_admin"] = bool(db_user["is_admin"])
    else:
      data["is_admin"] = False

    return await handler(event, data)
