import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATASET_DIR = BASE_DIR / "dataset"
LOGS_DIR = BASE_DIR / "logs"
DATASET_PATH = DATASET_DIR / "books.xlsx"

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
DATABASE_PATH = BASE_DIR / "data" / "books.db"

MOODS = ["веселое", "грустное", "напряженное"]

MOOD_LABELS = {
    "веселое": "😊 Весёлое",
    "грустное": "😢 Грустное",
    "напряженное": "😰 Напряжённое",
}

RATING_PREFERENCES = {
    "hits": "Только хиты (высокий рейтинг)",
    "any": "Готов читать новинки",
}

BOOK_LENGTHS = {
    "short": "Короткая (до 200 стр.)",
    "medium": "Средняя (200-400 стр.)",
    "long": "Длинная (400+ стр.)",
}

INTERESTS = [
    "Любовь",
    "Приключения",
    "Философия",
    "История",
    "Наука",
    "Психология",
    "Юмор",
    "Мистика",
]
