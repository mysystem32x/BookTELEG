from database.db import get_db


async def get_user(user_id):
  async with get_db() as db:
    db.row_factory = _dict_factory
    cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    return row


async def create_user(user_id, username, is_admin=False):
  async with get_db() as db:
    await db.execute(
      "INSERT OR IGNORE INTO users (user_id, username, is_admin) VALUES (?, ?, ?)",
      (user_id, username, int(is_admin)),
    )
    await db.commit()


async def set_admin(user_id, is_admin):
  async with get_db() as db:
    await db.execute(
      "UPDATE users SET is_admin = ? WHERE user_id = ?",
      (int(is_admin), user_id),
    )
    await db.commit()


async def save_preferences(user_id, genres, mood, rating_pref, book_length, interests):
  genres_str = ",".join(genres)
  interests_str = ",".join(interests)

  async with get_db() as db:
    await db.execute(
      """
      INSERT INTO user_preferences (user_id, genres, mood, rating_pref, book_length, interests)
      VALUES (?, ?, ?, ?, ?, ?)
      ON CONFLICT(user_id) DO UPDATE SET
        genres = excluded.genres,
        mood = excluded.mood,
        rating_pref = excluded.rating_pref,
        book_length = excluded.book_length,
        interests = excluded.interests
      """,
      (user_id, genres_str, mood, rating_pref, book_length, interests_str),
    )
    await db.commit()


async def get_preferences(user_id):
  async with get_db() as db:
    db.row_factory = _dict_factory
    cursor = await db.execute(
      "SELECT * FROM user_preferences WHERE user_id = ?",
      (user_id,),
    )
    row = await cursor.fetchone()
    if not row:
      return None

    return {
      "genres": row["genres"].split(",") if row["genres"] else [],
      "mood": row["mood"],
      "rating_pref": row["rating_pref"],
      "book_length": row["book_length"],
      "interests": row["interests"].split(",") if row["interests"] else [],
    }


async def get_read_history(user_id):
  async with get_db() as db:
    db.row_factory = _dict_factory
    cursor = await db.execute(
      """
      SELECT b.id, b.title, b.author, rh.read_at
      FROM read_history rh
      JOIN books b ON b.id = rh.book_id
      WHERE rh.user_id = ?
      ORDER BY rh.read_at DESC
      """,
      (user_id,),
    )
    return await cursor.fetchall()


async def add_to_history(user_id, book_id):
  async with get_db() as db:
    await db.execute(
      "INSERT INTO read_history (user_id, book_id) VALUES (?, ?)",
      (user_id, book_id),
    )
    await db.commit()


async def save_grade(user_id, book_id, grade):
  async with get_db() as db:
    await db.execute(
      """
      INSERT INTO book_grades (user_id, book_id, grade)
      VALUES (?, ?, ?)
      ON CONFLICT(user_id, book_id) DO UPDATE SET grade = excluded.grade
      """,
      (user_id, book_id, grade),
    )
    await db.commit()


async def get_stats():
  async with get_db() as db:
    db.row_factory = _dict_factory

    users = await (await db.execute("SELECT COUNT(*) as count FROM users")).fetchone()
    books = await (await db.execute("SELECT COUNT(*) as count FROM books")).fetchone()
    prefs = await (await db.execute("SELECT COUNT(*) as count FROM user_preferences")).fetchone()
    history = await (await db.execute("SELECT COUNT(*) as count FROM read_history")).fetchone()
    grades = await (await db.execute("SELECT COUNT(*) as count FROM book_grades")).fetchone()
    errors = await (await db.execute("SELECT COUNT(*) as count FROM error_logs")).fetchone()

    return {
      "users": users["count"],
      "books": books["count"],
      "preferences": prefs["count"],
      "history": history["count"],
      "grades": grades["count"],
      "errors": errors["count"],
    }


async def get_active_users():
  async with get_db() as db:
    db.row_factory = _dict_factory
    cursor = await db.execute(
      """
      SELECT u.user_id, u.username, u.is_admin, u.created_at,
             COUNT(rh.id) as books_read
      FROM users u
      LEFT JOIN read_history rh ON rh.user_id = u.user_id
      GROUP BY u.user_id
      ORDER BY books_read DESC
      """
    )
    return await cursor.fetchall()


def _dict_factory(cursor, row):
  columns = [col[0] for col in cursor.description]
  return dict(zip(columns, row))
