from aiogram.fsm.state import State, StatesGroup


class SurveyStates(StatesGroup):
  genres = State()


class AdminStates(StatesGroup):
  add_title = State()
  add_author = State()
  add_genre = State()
  add_mood = State()
  add_description = State()
  add_rating = State()
  add_pages = State()
  add_is_new = State()
  add_interests = State()

  delete_book_id = State()
  update_book_id = State()
  update_field = State()
  update_value = State()

  import_file = State()


class GradeStates(StatesGroup):
  choose_book = State()
