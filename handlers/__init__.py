from aiogram import Router

from handlers.start import router as start_router
from handlers.survey import router as survey_router
from handlers.recommendations import router as recommendations_router
from handlers.profile import router as profile_router
from handlers.history import router as history_router
from handlers.grade import router as grade_router
from handlers.admin import router as admin_router


def setup_routers():
  main_router = Router()
  main_router.include_router(start_router)
  main_router.include_router(survey_router)
  main_router.include_router(recommendations_router)
  main_router.include_router(profile_router)
  main_router.include_router(history_router)
  main_router.include_router(grade_router)
  main_router.include_router(admin_router)
  return main_router
