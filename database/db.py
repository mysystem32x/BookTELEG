import aiosqlite

from config import DATABASE_PATH, DATA_DIR, LOGS_DIR


async def init_db():
  DATA_DIR.mkdir(parents=True, exist_ok=True)
  LOGS_DIR.mkdir(parents=True, exist_ok=True)

  async with aiosqlite.connect(DATABASE_PATH) as db:
    await db.executescript("""
      CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        is_admin INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        genre TEXT NOT NULL,
        mood TEXT NOT NULL,
        description TEXT NOT NULL,
        rating REAL DEFAULT 0,
        pages INTEGER DEFAULT 300,
        is_new INTEGER DEFAULT 0,
        interests TEXT DEFAULT ''
      );

      CREATE TABLE IF NOT EXISTS user_preferences (
        user_id INTEGER PRIMARY KEY,
        genres TEXT DEFAULT '',
        mood TEXT DEFAULT '',
        rating_pref TEXT DEFAULT 'any',
        book_length TEXT DEFAULT 'medium',
        interests TEXT DEFAULT '',
        FOREIGN KEY (user_id) REFERENCES users(user_id)
      );

      CREATE TABLE IF NOT EXISTS read_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        read_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (book_id) REFERENCES books(id)
      );

      CREATE TABLE IF NOT EXISTS book_grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        grade INTEGER NOT NULL,
        graded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (book_id) REFERENCES books(id),
        UNIQUE(user_id, book_id)
      );

      CREATE TABLE IF NOT EXISTS error_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        error_text TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      );
    """)
    await db.commit()


def get_db():
  return aiosqlite.connect(DATABASE_PATH)
