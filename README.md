# Telegram-бот «Рекомендатор книг»

Бот задаёт 5 вопросов о предпочтениях и с помощью ML-модели (TF-IDF + косинусное сходство) подбирает топ-3 книги.

## Структура проекта

```
book_bot/
├── main.py                 # Точка входа
├── config.py               # Настройки и константы
├── requirements.txt
├── .env.example
├── database/
│   ├── db.py               # Подключение к SQLite
│   └── __init__.py
├── handlers/               # Обработчики команд
│   ├── start.py
│   ├── survey.py
│   ├── recommendations.py
│   ├── profile.py
│   ├── history.py
│   ├── grade.py
│   └── admin.py
├── keyboards/              # Клавиатуры
│   ├── user_keyboards.py
│   └── admin_keyboards.py
├── middlewares/            # Middleware
│   ├── auth_middleware.py
│   └── error_middleware.py
├── states/                 # FSM-состояния
│   └── survey_states.py
├── services/               # Бизнес-логика
│   ├── recommender.py      # ML-рекомендации
│   ├── book_service.py
│   └── user_service.py
├── utils/
│   └── messages.py
└── data/
    └── sample_books.json
```

## Установка

```bash
cd book_bot
pip install -r requirements.txt
cp .env.example .env
```

Укажите в `.env`:
- `BOT_TOKEN` — токен от [@BotFather](https://t.me/BotFather)
- `ADMIN_IDS` — ваш Telegram ID (через запятую)

## Запуск

```bash
python main.py
```

## Команды пользователя

| Команда | Описание |
|---------|----------|
| `/start` | Описание и начало опроса |
| `/help` | Справка |
| `/again` | Новая подборка по тем же предпочтениям |
| `/profile` | Просмотр/изменение предпочтений |
| `/random` | Случайная рекомендация |
| `/history` | Прочитанные книги |
| `/grade` | Оценить книгу (1-5) |

## Команды администратора

| Команда | Описание |
|---------|----------|
| `/add_book` | Добавить книгу |
| `/delete_book` | Удалить книгу |
| `/update_book` | Обновить книгу |
| `/create_admin` | Назначить админа |
| `/drop_admin` | Снять права админа |
| `/stats` | Статистика |
| `/export` | Выгрузка в CSV/JSON |
| `/import` | Загрузка из файла |
| `/users` | Список пользователей |
| `/logs` | Логи ошибок |

## ML-рекомендации

Модель строит текстовый профиль пользователя и каждой книги, затем считает косинусное сходство (scikit-learn). Дополнительно применяются фильтры по жанру, настроению, рейтингу и объёму.
