import csv
import json
import logging
from pathlib import Path

from config import DATASET_PATH
from database.db import get_db
from services.dataset_loader import load_books_from_xlsx

logger = logging.getLogger(__name__)


async def get_all_books():
  async with get_db() as db:
    db.row_factory = _dict_factory
    cursor = await db.execute("SELECT * FROM books")
    return await cursor.fetchall()


async def get_book_by_id(book_id):
  async with get_db() as db:
    db.row_factory = _dict_factory
    cursor = await db.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    return await cursor.fetchone()


async def add_book(book_data):
  async with get_db() as db:
    cursor = await db.execute(
      """
      INSERT INTO books (title, author, genre, mood, description, rating, pages, is_new, interests)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      """,
      (
        book_data["title"],
        book_data["author"],
        book_data["genre"],
        book_data["mood"],
        book_data["description"],
        book_data.get("rating", 0),
        book_data.get("pages", 300),
        int(book_data.get("is_new", 0)),
        book_data.get("interests", ""),
      ),
    )
    await db.commit()
    return cursor.lastrowid


async def delete_book(book_id):
  async with get_db() as db:
    await db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    await db.commit()


async def update_book(book_id, field, value):
  allowed_fields = ["title", "author", "genre", "mood", "description", "rating", "pages", "is_new", "interests"]
  if field not in allowed_fields:
    return False

  async with get_db() as db:
    query = f"UPDATE books SET {field} = ? WHERE id = ?"
    await db.execute(query, (value, book_id))
    await db.commit()
  return True


async def seed_books_from_dataset():
  books = await get_all_books()
  if books:
    return 0

  dataset_books = load_books_from_xlsx(DATASET_PATH)
  for book in dataset_books:
    await add_book(book)

  logger.info("Загружено %s книг из %s", len(dataset_books), DATASET_PATH)
  return len(dataset_books)


async def import_books(file_path):
  path = Path(file_path)
  if not path.exists():
    return 0

  if path.suffix == ".json":
    books = json.loads(path.read_text(encoding="utf-8"))
  elif path.suffix in (".xlsx", ".xls"):
    books = load_books_from_xlsx(path)
  else:
    books = []
    with open(path, encoding="utf-8") as file:
      reader = csv.DictReader(file)
      for row in reader:
        books.append(row)

  count = 0
  for book in books:
    await add_book(book)
    count += 1
  return count


async def export_books(file_path, file_format):
  books = await get_all_books()
  path = Path(file_path)

  if file_format == "json":
    clean_books = []
    for book in books:
      clean_books.append({
        "title": book["title"],
        "author": book["author"],
        "genre": book["genre"],
        "mood": book["mood"],
        "description": book["description"],
        "rating": book["rating"],
        "pages": book["pages"],
        "is_new": book["is_new"],
        "interests": book["interests"],
      })
    path.write_text(json.dumps(clean_books, ensure_ascii=False, indent=2), encoding="utf-8")
  else:
    fieldnames = ["title", "author", "genre", "mood", "description", "rating", "pages", "is_new", "interests"]
    with open(path, "w", encoding="utf-8", newline="") as file:
      writer = csv.DictWriter(file, fieldnames=fieldnames)
      writer.writeheader()
      for book in books:
        writer.writerow({key: book[key] for key in fieldnames})

  return len(books)


def _dict_factory(cursor, row):
  columns = [col[0] for col in cursor.description]
  return dict(zip(columns, row))
